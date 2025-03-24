from dbt_mcp.config.config import load_config
from dbt_mcp.semantic_layer.client import get_semantic_layer_fetcher

config = load_config()

def test_semantic_layer_list_metrics():
    semantic_layer_fetcher = get_semantic_layer_fetcher(config)
    metrics = semantic_layer_fetcher.list_metrics()
    assert len(metrics) > 0

def test_semantic_layer_list_dimensions():
    semantic_layer_fetcher = get_semantic_layer_fetcher(config)
    metrics = semantic_layer_fetcher.list_metrics()
    dimensions = semantic_layer_fetcher.get_dimensions(metrics=[metrics[0].name])
    assert len(dimensions) > 0

def test_semantic_layer_query_metrics():
    semantic_layer_fetcher = get_semantic_layer_fetcher(config)
    metrics = semantic_layer_fetcher.list_metrics()
    result = semantic_layer_fetcher.query_metrics(metrics=[metrics[0].name])
    assert result is not None

def test_semantic_layer_query_metrics_with_misspellings():
    semantic_layer_fetcher = get_semantic_layer_fetcher(config)
    result = semantic_layer_fetcher.query_metrics(["revehue"])
    assert result is not None
    assert "revenue" in result
