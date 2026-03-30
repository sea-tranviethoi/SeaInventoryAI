import json
from mcp import ClientSession
from mcp.client.sse import sse_client


async def call_tool(tool_name, args):

    async with sse_client("http://127.0.0.1:8000/sse") as (read, write):

        async with ClientSession(read, write) as session:

            await session.initialize()

            result = await session.call_tool(tool_name, args)

            # Attribute is camelCase: structuredContent (not structured_content)
            if result.structuredContent:
                return result.structuredContent

            # Fallback: parse JSON from text content
            if result.content:
                for item in result.content:
                    text = getattr(item, 'text', None)
                    if text:
                        try:
                            return json.loads(text)
                        except (json.JSONDecodeError, ValueError):
                            pass

            return {}


async def reorder_analysis(product_id):

    return await call_tool(
        "reorder_analysis",
        {"product_id": product_id}
    )
