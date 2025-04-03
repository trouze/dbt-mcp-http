from mcp.server.fastmcp import FastMCP

from dbt_mcp.config.config import Config
from dbt_mcp.semantic_layer.client import get_semantic_layer_fetcher
from dbt_mcp.semantic_layer.types import (
    DimensionToolResponse,
    EntityToolResponse,
    MetricToolResponse,
)


def register_sl_tools(dbt_mcp: FastMCP, config: Config) -> None:
    host = config.host
    if not host or not config.token or not config.environment_id:
        raise ValueError(
            "Host, token, and environment ID are required to use semantic layer tools. "
            + "To disable semantic layer tools, "
            + "set DISABLE_SEMANTIC_LAYER=true in your environment."
        )
    semantic_layer_fetcher = get_semantic_layer_fetcher(config)

    @dbt_mcp.tool()
    def list_metrics() -> list[MetricToolResponse]:
        """
        List all metrics from the dbt Semantic Layer
        """
        return semantic_layer_fetcher.list_metrics()

    @dbt_mcp.tool()
    def get_dimensions(metrics: list[str]) -> list[DimensionToolResponse]:
        """
        Get available dimensions for specified metrics

        Args:
            metrics: List of metric names
        """
        return semantic_layer_fetcher.get_dimensions(metrics=metrics)

    @dbt_mcp.tool()
    def get_entities(metrics: list[str]) -> list[EntityToolResponse]:
        """
        Get entities for a metric

        Args:
            metrics: List of metric names
        """
        return semantic_layer_fetcher.get_entities(metrics=metrics)

    @dbt_mcp.tool()
    def query_metrics(
        metrics: list[str],
        group_by: list[str] | None = None,
        time_grain: str | None = None,
        limit: int | None = None,
    ):
        """
        Query metrics with optional grouping and filtering

        Args:
            metrics: List of metric names
            group_by: Optional list of dimensions to group by
            time_grain: Optional time grain (DAY, WEEK, MONTH, QUARTER, YEAR)
            limit: Optional limit for number of results
        """
        return semantic_layer_fetcher.query_metrics(
            metrics, group_by, time_grain, limit
        )
