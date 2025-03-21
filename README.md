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
- `DISABLE_DBT_CLI`: Set this to `true` to disable dbt Core and dbt Cloud CLI MCP objects. Otherwise, they are enabled.
- `DISABLE_SEMANTIC_LAYER`: Set this to `true` to disable dbt Semantic Layer MCP objects. Otherwise, they are enabled.
- `DISABLE_DISCOVERY`: Set this to `true` to disable dbt Discovery API MCP objects. Otherwise, they are enabled.
- `DBT_HOST`: Your dbt Cloud instance hostname. This will look like an `Access URL` found [here](https://docs.getdbt.com/docs/cloud/about-cloud/access-regions-ip-addresses).
- `DBT_ENV_ID`: Your dbt environment ID
- `DBT_TOKEN`: Your personal access token or service token. Service token is required when using the Semantic Layer.
- `DBT_PROJECT_DIR`: The path to your dbt Project.
- `DBT_PATH`: The path to your dbt Core or dbt Cloud CLI executable. You can find your dbt executable by running `which dbt`.
- `DBT_EXECUTABLE_TYPE`: Set this to `core` if the `DBT_PATH` environment variable points toward dbt Core. Otherwise, dbt Cloud CLI is assumed


### Install in Claude Desktop

Follow [these](https://modelcontextprotocol.io/quickstart/user) instructions to add the `dbt-mcp` `claude_desktop_config.json` configuration. After you have gone through the [Setup](#setup) instructions. It can look like this. Be sure to replace `<path-to-this-directory>`:

```json
{
  "mcpServers": {
    "dbt": {
      "command": "<path-to-this-directory>/.venv/bin/mcp",
      "args": [
        "run",
        "<path-to-this-directory>/dbt_mcp/main.py"
      ]
    }
  }
}
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
