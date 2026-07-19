import asyncio
import json
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER = StdioServerParameters(
    command=sys.executable,               # wahi python jo .venv ka hai
    args=["-m", "worker.mcp_server.server"],
)

async def _call(tool: str, arguments: dict) -> str:
    async with stdio_client(SERVER) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(tool, arguments=arguments)
            return result.content[0].text if result.content else ""

def call_tool(tool: str, arguments: dict) -> str:
    """Sync wrapper — LangGraph nodes ke liye."""
    return asyncio.run(_call(tool, arguments))