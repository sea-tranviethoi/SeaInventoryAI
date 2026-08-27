from fastapi import FastAPI
from mcp.server.fastmcp import FastMCP
import sqlite3
import os

app = FastAPI()
mcp = FastMCP("inventory-server")
app.mount("/mcp", mcp)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "inventory.db")

def get_db():
    return sqlite3.connect(DB_PATH)

@mcp.tool()
def get_inventory(product_id: str):
    with get_db() as db:
        cur = db.cursor()
        cur.execute(
            "SELECT stock_qty FROM inventory WHERE product_id=?",
            (product_id,)
        )
        result = cur.fetchone()
    if result is None:
        return {"stock": 0}
    return {"stock": result[0]}

@mcp.tool()
def forecast_demand(product_id: str):
    with get_db() as db:
        cur = db.cursor()
        cur.execute(
            "SELECT quantity FROM sales_history WHERE product_id=?",
            (product_id,)
        )
        rows = cur.fetchall()
    quantities = [r[0] for r in rows]
    if not quantities:
        return {
            "avg_daily_sales": 0,
            "forecast_30_days": 0
        }
    avg = sum(quantities) / len(quantities)
    return {
        "avg_daily_sales": avg,
        "forecast_30_days": avg * 30
    }

@mcp.tool()
def reorder_analysis(product_id: str):
    with get_db() as db:
        cur = db.cursor()
        cur.execute(
            "SELECT stock_qty FROM inventory WHERE product_id=?",
            (product_id,)
        )
        row = cur.fetchone()
        stock = row[0] if row else None
        cur.execute(
            "SELECT quantity FROM sales_history WHERE product_id=?",
            (product_id,)
        )
        rows = cur.fetchall()

    quantities = [r[0] for r in rows]

    if stock is None:
        return {"error": "Product not found"}

    avg = sum(quantities)/len(quantities) if quantities else 0

    forecast_30 = avg * 30
    safety_stock = avg * 7

    recommended = forecast_30 + safety_stock
    reorder = max(0, int(recommended - stock))

    return {
        "stock": stock,
        "avg_daily_sales": avg,
        "forecast_30": forecast_30,
        "safety_stock": safety_stock,
        "recommended_stock": recommended,
        "reorder_qty": reorder
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
