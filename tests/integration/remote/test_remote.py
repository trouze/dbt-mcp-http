import pytest
from dbt_mcp.remote.tools import register_remote_tools
from dbt_mcp.config.config import load_config
from mcp.server.fastmcp import FastMCP


@pytest.mark.asyncio
async def test_remote_tool():
    config = load_config()
    dbt_mcp = FastMCP("Test")
    await register_remote_tools(dbt_mcp, config)
    assert "add" in [t.name for t in await dbt_mcp.list_tools()]
    result = await dbt_mcp.call_tool("add", {"a": "1", "b": "1"})
    assert len(result) == 1
    assert result[0].text == "2"