# dbt Semantic Layer GraphQL MCP Server

This is an MCP server that connects to the dbt Semantic Layer via GraphQL and provides tools to query metrics and dimensions.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

Run the server:

```bash
mcp run minimal_server.py
```

Or in development mode:

```bash
mcp dev minimal_server.py
```

### Using Environment Variables

You can provide connection details using environment variables:

```bash
DBT_HOST=semantic-layer.cloud.getdbt.com DBT_ENV_ID=your_env_id DBT_TOKEN=your_token mcp run minimal_server.py
```

Or when installing:

```bash
mcp install minimal_server.py -v DBT_HOST=semantic-layer.cloud.getdbt.com -v DBT_ENV_ID=your_env_id -v DBT_TOKEN=your_token
```

## Functions

1. Connect to the dbt Semantic Layer:

```python
connect(
    host="semantic-layer.cloud.getdbt.com",
    environment_id="123456",
    token="dbt_sa_xxx"
)
```

2. List all metrics:

```python
list_metrics()
```

3. Get dimensions for specific metrics:

```python
get_dimensions(metrics=["revenue", "orders"])
```

4. Get available time granularities for metrics:

```python
get_granularities(metrics=["revenue", "orders"])
```

5. Query metrics with grouping:

```python
query_metrics(
    metrics=["revenue", "orders"],
    group_by=["metric_time", "customer__country"],
    time_grain="MONTH",
    limit=10
)
```

## Examples

Basic query to get metrics by month:

```python
query_metrics(
    metrics=["revenue"],
    group_by=["metric_time"],
    time_grain="MONTH"
)
```

Group by a non-time dimension:

```python
query_metrics(
    metrics=["revenue", "orders"],
    group_by=["customer__country"]
)
```

Combine time and categorical dimensions:

```python
query_metrics(
    metrics=["revenue"],
    group_by=["metric_time", "customer__region"],
    time_grain="QUARTER",
    limit=20
)
```
