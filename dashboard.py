import streamlit as st
import sqlite3
import pandas as pd
import asyncio
import sys
import os
import concurrent.futures

def run_async(coro):
    def run_in_thread():
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        return asyncio.run(coro)
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(run_in_thread).result()

from my_mcp_client import call_tool
from agent import inventory_agent

st.title("AI Inventory Management Dashboard")

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "inventory.db")
conn = sqlite3.connect(DB_PATH)

inventory = pd.read_sql_query(
    "SELECT * FROM inventory",
    conn
)

sales = pd.read_sql_query(
    "SELECT * FROM sales_history",
    conn
)

st.subheader("Current Inventory")
st.dataframe(inventory)

product = st.selectbox(
    "Select product",
    inventory["product_id"]
)

product_sales = sales[sales["product_id"] == product]

st.subheader("Sales History")
st.line_chart(product_sales.set_index("date")["quantity"])

result = run_async(
    call_tool(
        "forecast_demand",
        {"product_id": product}
    )
)

avg_daily_sales = result.get("avg_daily_sales", 0)
forecast_30 = result.get("forecast_30_days", 0)

stock = inventory[inventory["product_id"] == product]["stock_qty"].values[0]

st.subheader("AI Demand Forecast")

st.write("Average daily sales:", round(avg_daily_sales, 2))
st.write("Forecast next 30 days:", round(forecast_30, 2))
st.write("Current stock:", stock)

safety_stock = avg_daily_sales * 7
recommended_stock = forecast_30 + safety_stock

reorder_qty = max(0, int(recommended_stock - stock))

st.subheader("Inventory Recommendation")

st.write("Safety stock:", round(safety_stock, 2))
st.write("Recommended inventory level:", round(recommended_stock, 2))
st.write("Reorder quantity:", reorder_qty)

if reorder_qty > 0:
    st.error("⚠ Reorder required")
else:
    st.success("Stock level OK")

question = st.text_input("Ask AI about inventory")

if question:

    answer = run_async(
        inventory_agent(product, question)
    )

    st.write(answer)
