import asyncio
import json

from openai import OpenAI
from openai.types.responses.response_input_param import FunctionCallOutput

from client.tools import get_tools
from dbt_mcp.config.config import load_config
from dbt_mcp.mcp.server import dbt_mcp

LLM_MODEL = "gpt-4o-mini"
llm_client = OpenAI()
config = load_config()
messages = []


async def main():
    while True:
        user_input = input("> ")
        messages.append({"role": "user", "content": user_input})
        response = llm_client.responses.create(
            model=LLM_MODEL,
            input=messages,
            tools=await get_tools(),
            parallel_tool_calls=False,
        )
        tool_call = response.output[0]
        print(f"Calling tool: {tool_call.name} with arguments: {tool_call.arguments}")
        tool_response = await dbt_mcp.call_tool(
            tool_call.name,
            json.loads(tool_call.arguments),
        )
        print(f"Tool response: {tool_response}")
        messages.append(tool_call)
        messages.append(
            FunctionCallOutput(
                type="function_call_output",
                call_id=tool_call.call_id,
                output=str(tool_response),
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
