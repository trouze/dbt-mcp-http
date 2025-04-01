import pytest
from dbt_mcp.remote.tools import register_remote_tools
from dbt_mcp.config.config import load_config
from mcp.server.fastmcp import FastMCP


@pytest.mark.asyncio
async def test_remote_tool():
    config = load_config()
    dbt_mcp = FastMCP("Test")
    await register_remote_tools(dbt_mcp, config)
    assert "echo_tool" in [t.name for t in await dbt_mcp.list_tools()]
    result = await dbt_mcp.call_tool("echo_tool", {"message": "Hello, world!"})
    assert len(result) == 1
    assert "Hello, world!" in result[0].text
