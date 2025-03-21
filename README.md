# dbt MCP Server

A MCP (Model Context Protocol) server for interacting with dbt resources.

## Setup

1. Clone the repository:
```shell
git clone https://github.com/dbt-labs/dbt-mcp-prototype.git
cd dbt-mcp-prototype
```

2. [Install uv](https://docs.astral.sh/uv/getting-started/installation/)

3. Run `uv sync`

4. Configure environment variables:
```shell
cp .env.example .env
```
Then edit `.env` with your specific environment variables:
- `DISABLE_DBT_CORE`: Set this to `true` to disable dbt Core MCP objects. Otherwise, they are enabled.
- `DISABLE_SEMANTIC_LAYER`: Set this to `true` to disable dbt Semantic Layer MCP objects. Otherwise, they are enabled.
- `DISABLE_DISCOVERY`: Set this to `true` to disable dbt Discovery API MCP objects. Otherwise, they are enabled.
- `DBT_HOST`: Your dbt Cloud instance hostname. This will look like an `Access URL` found [here](https://docs.getdbt.com/docs/cloud/about-cloud/access-regions-ip-addresses).
- `DBT_ENV_ID`: Your dbt environment ID
- `DBT_TOKEN`: Your personal access token or service token. Service token is required when using the Semantic Layer.
- `DBT_PROJECT_DIR`: The path to your dbt Project.
- `DBT_PATH`: The path to your dbt executable.


### Install in Claude Desktop

```shell
mcp install dbt_mcp/main.py --name "dbt" --with "mcp[cli]" --with "requests>=2.31.0" --with "python-dotenv>=1.0.0"
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

### Local development

- Run the development server:
```shell
mcp dev dbt_mcp/main.py --with "mcp[cli]" --with "requests>=2.31.0" --with "python-dotenv>=1.0.0"
```

- Run inspector:
```shell
npx @modelcontextprotocol/inspector mcp run dbt_mcp/main.py
```
