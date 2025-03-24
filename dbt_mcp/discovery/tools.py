from mcp.server.fastmcp import FastMCP
from dbt_mcp.config.config import Config
from dbt_mcp.discovery.client import MetadataAPIClient, ModelsFetcher

def register_discovery_tools(dbt_mcp: FastMCP, config: Config) -> None:
    api_client = MetadataAPIClient(config.host, config.token)
    models_fetcher = ModelsFetcher(api_client, config.environment_id)

    @dbt_mcp.tool()
    def get_mart_models() -> list[dict]:
        """
        Get the name and description of all mart models in the environment. A mart model is part of the presentation layer of the dbt project. It's where cleaned, transformed data is organized for consumption by end-users, like analysts, dashboards, or business tools.
        """
        mart_models = models_fetcher.fetch_models(model_filter={"modelingLayer": "marts"})
        return [m for m in mart_models if m["name"] != "metricflow_time_spine"]


    @dbt_mcp.tool()
    def get_all_models() -> list[dict]:
        """
        Get the name and description of all dbt models in the environment.
        """
        return models_fetcher.fetch_models()

    @dbt_mcp.tool()
    def get_model_details(model_name: str) -> dict:
        """
        Retrieves information about a specific dbt model. Specifically, it returns the compiled sql, description, column names, column descriptions, and column types.

        Args:
            model_name: The name of the dbt model to retrieve details for.
        """
        return models_fetcher.fetch_model_details(model_name)

    @dbt_mcp.tool()
    def get_model_parents(model_name: str) -> list[dict]:
        """
        Get the parents of a specific dbt model.
        """
        return models_fetcher.fetch_model_parents(model_name)
