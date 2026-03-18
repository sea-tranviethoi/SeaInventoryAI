from mcp import ClientSession
from mcp.client.sse import sse_client

async def call_tool(tool_name, args):

    async with sse_client("http://127.0.0.1:8000/mcp") as (read, write):

        async with ClientSession(read, write) as session:

            await session.initialize()

            result = await session.call_tool(tool_name, args)

            if result.structured_content:
                return result.structured_content

            return {}


async def reorder_analysis(product_id):

    return await call_tool(
        "reorder_analysis",
        {"product_id": product_id}
    )
