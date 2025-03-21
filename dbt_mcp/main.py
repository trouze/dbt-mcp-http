import os
from mcp.server.fastmcp import FastMCP
from config.config import load_config
from semantic_layer.tools import register_sl_tools
from discovery.tools import register_discovery_tools
from dbt_core.tools import register_dbt_core_tools

dbt_mcp = FastMCP("dbt")

config = load_config()

if config.semantic_layer_enabled:
    register_sl_tools(dbt_mcp, config)

if config.discovery_enabled:
    register_discovery_tools(dbt_mcp, config)

if config.dbt_core_enabled:
    register_dbt_core_tools(dbt_mcp, config)

print("Starting dbt MCP server")
dbt_mcp.run()
