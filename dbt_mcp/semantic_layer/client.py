from contextlib import contextmanager
from functools import cache, lru_cache
from typing import Any, Generator, LiteralString, Protocol

from dbtsl import SemanticLayerClient
from dbt_mcp.config.config import Config
from dbt_mcp.semantic_layer.levenshtein import get_misspellings
from dbt_mcp.semantic_layer.types import DimensionToolResponse, MetricToolResponse
from dbtsl.models.dimension import Dimension
from dbtsl.models.metric import Metric
import time
import requests

class SemanticLayerClientProtocol(Protocol):
    @contextmanager
    def session(self) -> Generator[Any, Any, None]:
        ...

    def metrics(self) -> list[Metric]:
        ...

    def dimensions(self, metrics: list[str]) -> list[Dimension]:
        ...

class SemanticLayerFetcher:
    def __init__(self, sl_client: SemanticLayerClientProtocol, host: str, config: Config):
        self.sl_client = sl_client
        self.host = host
        self.config = config
        self.dimensions_cache = {}

    @cache
    def list_metrics(self) -> list[MetricToolResponse]:
        with self.sl_client.session():
            return [
                MetricToolResponse(
                    name=m.name,
                    type=m.type,
                    label=m.label,
                    description=m.description,
                )
                for m in self.sl_client.metrics()
            ]

    def get_dimensions(self, metrics: list[str]) -> list[DimensionToolResponse]:
        metrics_key = ",".join(sorted(metrics))
        if metrics_key not in self.dimensions_cache:
            with self.sl_client.session():
                self.dimensions_cache[metrics_key] = [
                    DimensionToolResponse(
                        name=d.name,
                        type=d.type,
                        description=d.description,
                        label=d.label,
                        granularities=d.queryable_time_granularities
                    )
                    for d in self.sl_client.dimensions(metrics=metrics)
                ]
        return self.dimensions_cache[metrics_key]

    def validate_query_metrics_params(
        self,
        metrics: list[str],
        group_by: list[str] | None
    ) -> LiteralString | None:
        errors = []
        available_metrics_names = [m.name for m in self.list_metrics()]
        metric_misspellings = get_misspellings(
            targets=metrics,
            words=available_metrics_names,
            top_k=5,
        )
        for metric_misspelling in metric_misspellings:
            recommendations = " Did you mean: " + ", ".join(metric_misspelling.similar_words) + "?"
            errors.append(
                f"Metric {metric_misspelling.word} not found." + recommendations if metric_misspelling.similar_words else ""
            )

        if errors:
            return "Errors: " + ", ".join(errors)

        available_dimensions = [d.name for d in self.get_dimensions(metrics)]
        dimension_misspellings = get_misspellings(
            targets=group_by or [],
            words=available_dimensions,
            top_k=5,
        )
        for dimension_misspelling in dimension_misspellings:
            recommendations = " Did you mean: " + ", ".join(dimension_misspelling.similar_words) + "?"
            errors.append(
                f"Dimension {dimension_misspelling.word} not found." + recommendations if dimension_misspelling.similar_words else ""
            )

        if errors:
            return "Errors: " + ", ".join(errors)

    def query_metrics(
        self,
        metrics: list[str],
        group_by: list[str] | None = None,
        time_grain: str | None = None,
        limit: int | None = None
    ):
        error_message = self.validate_query_metrics_params(
            metrics=metrics,
            group_by=group_by,
        )
        if error_message:
            return error_message

        # Generate metric list string for GraphQL
        metric_list = ", ".join([f"{{name: \"{metric}\"}}" for metric in metrics])

        # Build group_by section if needed
        group_by_section = ""
        if group_by:
            groups = []
            for dim in group_by:
                if dim == "metric_time" and time_grain:
                    groups.append(f'{{name: "{dim}", grain: {time_grain}}}')
                else:
                    groups.append(f'{{name: "{dim}"}}')
            group_by_section = f"groupBy: [{', '.join(groups)}]"

        # Build limit section if needed
        limit_section = f"limit: {limit}" if limit else ""

        # Build create query mutation with direct string construction
        mutation = f"""
        mutation {{
        createQuery(
            environmentId: "{self.config.environment_id}"
            metrics: [{metric_list}]
            {group_by_section}
            {limit_section}
        ) {{
            queryId
        }}
        }}
        """

        url = f"https://{self.host}/api/graphql"
        headers = {"Authorization": f"Bearer {self.config.token}"}

        print(f"Executing GraphQL mutation: {mutation}")

        # Execute create query mutation
        response = requests.post(
            url,
            headers=headers,
            json={"query": mutation}
        )
        response.raise_for_status()
        create_data = response.json()

        if "errors" in create_data:
            return f"GraphQL error: {create_data['errors']}"

        # Get query ID
        query_id = create_data["data"]["createQuery"]["queryId"]

        # Poll for results
        max_attempts = 30
        attempts = 0
        query_result = None

        while attempts < max_attempts:
            attempts += 1

            # Query for results
            result_query = f"""
            {{
            query(environmentId: "{self.config.environment_id}", queryId: "{query_id}") {{
                status
                error
                jsonResult(encoded: false)
            }}
            }}
            """

            print(f"Polling with query: {result_query}")

            response = requests.post(
                url,
                headers=headers,
                json={"query": result_query}
            )
            response.raise_for_status()
            result_data = response.json()

            if "errors" in result_data:
                return f"GraphQL error: {result_data['errors']}"

            query_result = result_data["data"]["query"]

            # Check status
            if query_result["status"] == "FAILED":
                return f"Query failed: {query_result['error']}"
            elif query_result["status"] == "SUCCESSFUL":
                break

            # Wait before polling again
            time.sleep(1)

        if attempts >= max_attempts:
            return "Query timed out. Please try again or simplify your query."

        # Parse and return results
        if query_result["jsonResult"]:
            # Return the raw JSON result
            return query_result["jsonResult"]
        else:
            return "No results returned."

def get_semantic_layer_fetcher(config: Config) -> SemanticLayerFetcher:
    host = f"semantic-layer.{config.host}"
    semantic_layer_client = SemanticLayerClient(
        environment_id=config.environment_id,
        auth_token=config.token,
        host=host,
    )
    return SemanticLayerFetcher(
        sl_client=semantic_layer_client,
        host=host,
        config=config,
    )
