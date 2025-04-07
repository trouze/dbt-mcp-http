from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import (
    Annotated,
    Any,
)

import httpcore
import httpx
from mcp.client.session import ClientSession
from mcp.client.sse import sse_client
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.tools.base import Tool
from mcp.server.fastmcp.utilities.func_metadata import (
    ArgModelBase,
    FuncMetadata,
    _get_typed_annotation,
)
from mcp.types import EmbeddedResource, ImageContent, TextContent
from mcp.types import Tool as RemoteTool
from pydantic import Field, WithJsonSchema, create_model
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined

from dbt_mcp.config.config import Config


@asynccontextmanager
async def sse_mcp_connection_context(
    url: str,
    headers: dict[str, Any] | None = None,
    timeout: float = 5,
    sse_read_timeout: float = 60 * 5,
) -> AsyncGenerator[ClientSession, None]:
    async with (
        sse_client(url, headers, timeout, sse_read_timeout) as (read, write),
        ClientSession(read, write) as session,
    ):
        await session.initialize()
        yield session


# Based on this: https://github.com/modelcontextprotocol/python-sdk/blob/9ae4df85fbab97bf476ddd160b766ca4c208cd13/src/mcp/server/fastmcp/utilities/func_metadata.py#L105
def get_remote_tool_fn_metadata(tool: RemoteTool) -> FuncMetadata:
    dynamic_pydantic_model_params: dict[str, Any] = {}
    for key in tool.inputSchema["properties"].keys():
        # Remote tools shouldn't have type annotations or default values
        # for their arguments. So, we set them to defaults.
        field_info = FieldInfo.from_annotated_attribute(
            annotation=_get_typed_annotation(
                annotation=Annotated[
                    Any,
                    Field(),
                    WithJsonSchema({"title": key, "type": "string"}),
                ],
                globalns={},
            ),
            default=PydanticUndefined,
        )
        dynamic_pydantic_model_params[key] = (field_info.annotation, None)
    return FuncMetadata(
        arg_model=create_model(
            f"{tool.name}Arguments",
            **dynamic_pydantic_model_params,
            __base__=ArgModelBase,
        )
    )


async def list_remote_tools(
    url: str,
    headers: dict[str, Any],
) -> list[RemoteTool]:
    result: list[RemoteTool] = []
    try:
        async with sse_mcp_connection_context(url, headers) as session:
            result = (await session.list_tools()).tools
    except* (
        httpx.ConnectError,
        httpx.ReadTimeout,
        httpx.ConnectTimeout,
        httpcore.ConnectTimeout,
        httpx.RemoteProtocolError,
    ) as e:
        print(f"Connection error while listing remote tools: {e}")
    return result


async def register_remote_tools(dbt_mcp: FastMCP, config: Config) -> None:
    headers = {
        "Authorization": f"Bearer {config.token}",
        "environmentId": str(config.environment_id),
    }
    remote_tools = await list_remote_tools(config.remote_mcp_url, headers)
    for tool in remote_tools:
        # Create a new function using a factory to avoid closure issues
        def create_tool_function(tool_name: str):
            async def tool_function(
                *args, **kwargs
            ) -> list[TextContent | ImageContent | EmbeddedResource]:
                async with sse_mcp_connection_context(
                    config.remote_mcp_url, headers
                ) as session:
                    return (
                        await session.call_tool(name=tool_name, arguments=kwargs)
                    ).content

            return tool_function

        new_tool = create_tool_function(tool.name)
        dbt_mcp._tool_manager._tools[tool.name] = Tool(
            fn=new_tool,
            name=tool.name,
            description=tool.description or "",
            parameters=tool.inputSchema,
            fn_metadata=get_remote_tool_fn_metadata(tool),
            is_async=True,
            # `tool_function` doesn't currently have a
            # `ctx: Context` parameter, so this is None.
            # See this: https://github.com/modelcontextprotocol/python-sdk/blob/9ae4df85fbab97bf476ddd160b766ca4c208cd13/README.md?plain=1#L283
            context_kwarg=None,
        )
