import asyncio
import sys
import traceback
from mcp import ClientSession
from mcp.client.sse import sse_client

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def test():
    try:
        async with sse_client("http://127.0.0.1:8000/sse") as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                print("Connected successfully!")
                result = await session.call_tool("reorder_analysis", {"product_id": "A001"})
                print("Result:", result)
    except ExceptionGroup as eg:
        print(f"\n=== ExceptionGroup: {eg} ===")
        for i, exc in enumerate(eg.exceptions):
            print(f"\n--- Sub-exception {i+1}: {type(exc).__name__}: {exc} ---")
            traceback.print_exception(type(exc), exc, exc.__traceback__)
    except Exception as e:
        print(f"\n=== Exception: {type(e).__name__}: {e} ===")
        traceback.print_exc()

asyncio.run(test())
