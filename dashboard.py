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

TRANSLATIONS = {
    "en": {
        "title": "AI Inventory Management Dashboard",
        "current_inventory": "Current Inventory",
        "select_product": "Select product",
        "sales_history": "Sales History",
        "ai_forecast": "AI Demand Forecast",
        "avg_daily_sales": "Average daily sales:",
        "forecast_30": "Forecast next 30 days:",
        "current_stock": "Current stock:",
        "recommendation": "Inventory Recommendation",
        "safety_stock": "Safety stock:",
        "recommended_level": "Recommended inventory level:",
        "reorder_qty": "Reorder quantity:",
        "reorder_required": "⚠ Reorder required",
        "stock_ok": "Stock level OK",
        "ask_ai": "Ask AI about inventory",
        "select_language": "Language",
    },
    "vi": {
        "title": "Bảng Quản Lý Kho Hàng AI",
        "current_inventory": "Tồn Kho Hiện Tại",
        "select_product": "Chọn sản phẩm",
        "sales_history": "Lịch Sử Bán Hàng",
        "ai_forecast": "Dự Báo Nhu Cầu AI",
        "avg_daily_sales": "Doanh số trung bình mỗi ngày:",
        "forecast_30": "Dự báo 30 ngày tới:",
        "current_stock": "Tồn kho hiện tại:",
        "recommendation": "Khuyến Nghị Nhập Hàng",
        "safety_stock": "Tồn kho an toàn:",
        "recommended_level": "Mức tồn kho khuyến nghị:",
        "reorder_qty": "Số lượng cần nhập:",
        "reorder_required": "⚠ Cần nhập hàng",
        "stock_ok": "Tồn kho ổn định",
        "ask_ai": "Hỏi AI về kho hàng",
        "select_language": "Ngôn ngữ",
    },
    "ja": {
        "title": "AI在庫管理ダッシュボード",
        "current_inventory": "現在の在庫",
        "select_product": "商品を選択",
        "sales_history": "販売履歴",
        "ai_forecast": "AI需要予測",
        "avg_daily_sales": "平均日次売上：",
        "forecast_30": "今後30日間の予測：",
        "current_stock": "現在の在庫数：",
        "recommendation": "在庫補充の推奨",
        "safety_stock": "安全在庫：",
        "recommended_level": "推奨在庫レベル：",
        "reorder_qty": "発注数量：",
        "reorder_required": "⚠ 発注が必要です",
        "stock_ok": "在庫は十分です",
        "ask_ai": "在庫についてAIに質問する",
        "select_language": "言語",
    },
}

lang = st.sidebar.selectbox(
    "Language / Ngôn ngữ / 言語",
    options=["en", "vi", "ja"],
    format_func=lambda x: {"en": "English", "vi": "Tiếng Việt", "ja": "日本語"}[x]
)
t = TRANSLATIONS[lang]

st.title(t["title"])

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

st.subheader(t["current_inventory"])
st.dataframe(inventory)

product = st.selectbox(
    t["select_product"],
    inventory["product_id"]
)

product_sales = sales[sales["product_id"] == product]

st.subheader(t["sales_history"])
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

st.subheader(t["ai_forecast"])

st.write(t["avg_daily_sales"], round(avg_daily_sales, 2))
st.write(t["forecast_30"], round(forecast_30, 2))
st.write(t["current_stock"], stock)

safety_stock = avg_daily_sales * 7
recommended_stock = forecast_30 + safety_stock

reorder_qty = max(0, int(recommended_stock - stock))

st.subheader(t["recommendation"])

st.write(t["safety_stock"], round(safety_stock, 2))
st.write(t["recommended_level"], round(recommended_stock, 2))
st.write(t["reorder_qty"], reorder_qty)

if reorder_qty > 0:
    st.error(t["reorder_required"])
else:
    st.success(t["stock_ok"])

question = st.text_input(t["ask_ai"])

if question:

    answer = run_async(
        inventory_agent(product, question)
    )

    st.write(answer)
