import os
from dbtsl import SemanticLayerClient
from config.config import Config
from semantic_layer.types import MetricToolResponse
import time
from mcp.server.fastmcp import FastMCP
import requests
from semantic_layer.types import DimensionToolResponse, MetricToolResponse

def register_sl_tools(dbt_mcp: FastMCP, config: Config) -> None:
    sl_host = f"semantic-layer.{config.host}"

    semantic_layer_client = SemanticLayerClient(
        environment_id=config.environment_id,
        auth_token=config.token,
        host=sl_host,
    )

    @dbt_mcp.tool()
    def list_metrics() -> list[MetricToolResponse]:
        """
        List all metrics from the dbt Semantic Layer
        """
        with semantic_layer_client.session():
            return [
                MetricToolResponse(
                    name=m.name,
                    type=m.type,
                    label=m.label,
                    description=m.description,
                )
                for m in semantic_layer_client.metrics()
            ]

    @dbt_mcp.tool()
    def get_dimensions(metrics: list[str]) -> list[DimensionToolResponse]:
        """
        Get available dimensions for specified metrics

        Args:
            metrics: List of metric names or a single metric name
        """
        with semantic_layer_client.session():
            return [
                DimensionToolResponse(
                    name=d.name,
                    type=d.type,
                    description=d.description,
                    label=d.label,
                    granularities=d.queryable_time_granularities
                )
                for d in semantic_layer_client.dimensions(metrics=metrics)
            ]

    @dbt_mcp.tool()
    def query_metrics(
        metrics: list[str],
        group_by: list[str] | None = None,
        time_grain: str | None = None,
        limit: int | None = None
    ):
        """
        Query metrics with optional grouping and filtering

        Args:
            metrics: List of metric names
            group_by: Optional list of dimensions to group by
            time_grain: Optional time grain (DAY, WEEK, MONTH, QUARTER, YEAR)
            limit: Optional limit for number of results
        """
        try:
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
                environmentId: "{config.environment_id}"
                metrics: [{metric_list}]
                {group_by_section}
                {limit_section}
            ) {{
                queryId
            }}
            }}
            """

            url = f"https://{sl_host}/api/graphql"
            headers = {"Authorization": f"Bearer {config.token}"}

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
                query(environmentId: "{config.environment_id}", queryId: "{query_id}") {{
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
        except Exception as e:
            return f"Error querying metrics: {str(e)}"
