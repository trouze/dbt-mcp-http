from mcp.server.fastmcp import FastMCP
from semantic_layer.tools import register_sl_tools

dbt_mcp = FastMCP("dbt")

register_sl_tools(dbt_mcp)

dbt_mcp.run()