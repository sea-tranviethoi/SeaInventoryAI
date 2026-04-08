import sys
import requests
from my_mcp_client import reorder_analysis

if sys.platform == "win32":
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


def ask_llama(prompt):

    r = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        }
    )

    return r.json().get("response", "")


async def inventory_agent(product_id, question):

    data = await reorder_analysis(product_id)
    print("DEBUG TOOL RESULT:", data)
    
    stock = data.get("stock", 0)
    reorder_qty = data.get("reorder_qty", 0)
    forecast_30 = data.get("forecast_30", 0)
    avg_sales = data.get("avg_daily_sales", 0)

    # 🔴 Python quyết định
    if reorder_qty > 0:
        decision = "REORDER"
    else:
        decision = "NO REORDER"

    prompt = f"""
You are an inventory AI assistant.

Product: {product_id}

Current stock: {stock}
Average daily sales: {avg_sales}
Forecast next 30 days: {forecast_30}
Reorder quantity needed: {reorder_qty}

Decision already calculated:
{decision}

Explain the reason in one short sentence.
"""

    reason = ask_llama(prompt)

    return f"Decision: {decision}\nReason: {reason}"
