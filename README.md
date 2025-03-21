# dbt MCP Minimal Server

A minimal MCP (Metrics Control Plane) server for interacting with the dbt Semantic Layer.

## Requirements

- Python 3.12+
- dbt Semantic Layer access

## Setup

1. Clone the repository:
```bash
git clone https://github.com/dbt-labs/dbt-mcp-prototype.git
cd dbt-mcp-prototype
```

2. Set up your Python environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install --upgrade pip
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

### Install

```shell
mcp install main.py --name "dbt" --with "mcp[cli]" --with "requests>=2.31.0" --with "python-dotenv>=1.0.0"
```

This command will add an entry like the following to `claude_desktop_config.json`:

```json
    "dbt": {
      "command": "uv",
      "args": [
        "run",
        "--with",
        "mcp[cli]",
        "--with",
        "python-dotenv>=1.0.0",
        "--with",
        "requests",
        "mcp",
        "run",
        "/YOUR_INSTALL_PATH/dbt-mcp-prototype/main.py"
      ]
    },
```

Assuming `EDITOR` environment variable is configured and standard install location of Claude Desktop for macOS, you can examine it like this:

```shell
$EDITOR ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

## Usage

Currently implemented commands:
- `list_metrics()`: List all available metrics

Stub commands (to be implemented):
- `get_dimensions(metrics)`: Get available dimensions for specified metrics
- `get_granularities(metrics)`: Get available time granularities for metrics
- `query_metrics(metrics, group_by=None, time_grain=None, limit=None)`: Query metrics with optional grouping and filtering

### Local development

```shell
mcp dev minimal_server.py --with "mcp[cli]" --with "requests>=2.31.0" --with "python-dotenv>=1.0.0"
```
