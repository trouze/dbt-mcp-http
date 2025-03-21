import os
from mcp.server.fastmcp import FastMCP
from config.config import load_config
from semantic_layer.tools import register_sl_tools
from discovery.tools import register_discovery_tools

dbt_mcp = FastMCP("dbt")

config = load_config()

if os.getenv("DISABLE_SEMANTIC_LAYER") != "true":
    register_sl_tools(dbt_mcp, config)

if os.getenv("DISABLE_DISCOVERY") != "true":
    register_discovery_tools(dbt_mcp, config)

print("Starting dbt MCP server")
dbt_mcp.run()
