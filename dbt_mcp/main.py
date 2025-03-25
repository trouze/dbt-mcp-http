import asyncio
import mcp
from mcp.server.fastmcp import FastMCP
from config.config import load_config
from dbt_mcp.remote.tools import register_remote_tools
from semantic_layer.tools import register_sl_tools
from discovery.tools import register_discovery_tools
from dbt_cli.tools import register_dbt_cli_tools

dbt_mcp = FastMCP("dbt")

config = load_config()

if config.semantic_layer_enabled:
    register_sl_tools(dbt_mcp, config)

if config.discovery_enabled:
    register_discovery_tools(dbt_mcp, config)

if config.dbt_cli_enabled:
    register_dbt_cli_tools(dbt_mcp, config)

if config.remote_enabled:
    asyncio.run(register_remote_tools(dbt_mcp, config))

print("Starting dbt MCP server")
dbt_mcp.run()
