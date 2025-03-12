# dbt MCP Minimal Server

A minimal MCP (Metrics Control Plane) server for interacting with the dbt Semantic Layer.

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd dbt-mcp-minimal
```

2. Set up your Python environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
```
Then edit `.env` with your dbt Semantic Layer credentials:
- `DBT_HOST`: Your dbt Semantic Layer host
- `DBT_ENV_ID`: Your dbt environment ID
- `DBT_TOKEN`: Your service token

## Usage

Run the server:
```bash
python minimal_server.py
```

Available commands:
- `list_metrics()`: List all available metrics
- `get_dimensions(metrics)`: Get available dimensions for specified metrics
- `get_granularities(metrics)`: Get available time granularities for metrics
- `query_metrics(metrics, group_by=None, time_grain=None, limit=None)`: Query metrics with optional grouping and filtering

## Requirements

- Python 3.7+
- dbt Semantic Layer access
