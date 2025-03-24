from unittest.mock import MagicMock
from dbt_mcp.semantic_layer.client import SemanticLayerFetcher
from tests.unit.mocks import MockSemanticLayerClient
from dbtsl.models.metric import Metric, MetricType

def test_semantic_layer_fetcher_misspellings() -> None:
    mock_client = MockSemanticLayerClient(
        metrics=[Metric(
            name="revenue",
            type=MetricType.SIMPLE,
            description="Revenue",
            dimensions=[],
            measures=[],
            entities=[],
            queryable_granularities=[],
            queryable_time_granularities=[],
            label="Revenue",
            requires_metric_time=False
        )],
    )
    fetcher = SemanticLayerFetcher(mock_client, "fake", MagicMock())
    result = fetcher.validate_query_metrics_params(["revehue"], None)
    assert result is not None
    assert "revenue" in result
