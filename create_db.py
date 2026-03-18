import sqlite3
import random
from datetime import datetime, timedelta

conn = sqlite3.connect("inventory.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS products(
    product_id TEXT PRIMARY KEY,
    name TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS sales_history(
    product_id TEXT,
    date TEXT,
    quantity INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS inventory(
    product_id TEXT,
    stock_qty INTEGER
)
""")

products = [
    ("A001", "Keyboard"),
    ("A002", "Mouse"),
    ("A003", "Monitor")
]

cursor.executemany("INSERT OR REPLACE INTO products VALUES (?,?)", products)

for product in products:
    for i in range(60):
        date = datetime.now() - timedelta(days=i)
        qty = random.randint(5, 30)

        cursor.execute(
            "INSERT INTO sales_history VALUES (?,?,?)",
            (product[0], date.strftime("%Y-%m-%d"), qty)
        )

cursor.executemany(
    "INSERT OR REPLACE INTO inventory VALUES (?,?)",
    [
        ("A001", 120),
        ("A002", 80),
        ("A003", 45)
    ]
)

conn.commit()
conn.close()
