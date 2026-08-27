import sqlite3
import random
import os
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "inventory.db")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS products(
    product_id TEXT PRIMARY KEY,
    name TEXT,
    category TEXT
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

# Thêm cột category nếu chưa có
try:
    cursor.execute("ALTER TABLE products ADD COLUMN category TEXT")
except Exception:
    pass

# Xóa dữ liệu cũ
cursor.execute("DELETE FROM products")
cursor.execute("DELETE FROM sales_history")
cursor.execute("DELETE FROM inventory")

products = [
    # Makeup (10)
    ("MKP001", "Kem Nền Dưỡng Ẩm SPF30", "Makeup"),
    ("MKP002", "Che Khuyết Điểm Lâu Trôi", "Makeup"),
    ("MKP003", "Son Môi Lì Màu Đỏ Ruby", "Makeup"),
    ("MKP004", "Mascara Dày Mi Cong", "Makeup"),
    ("MKP005", "Kẻ Mắt Nước Đen Siêu Mảnh", "Makeup"),
    ("MKP006", "Bảng Phấn Mắt 12 Màu", "Makeup"),
    ("MKP007", "Phấn Má Hồng Tự Nhiên", "Makeup"),
    ("MKP008", "Phấn Bronzer Tạo Khối", "Makeup"),
    ("MKP009", "Phấn Phủ Kiềm Dầu", "Makeup"),
    ("MKP010", "Chì Kẻ Môi Lâu Trôi", "Makeup"),

    # Skincare (10)
    ("SKC001", "Serum Vitamin C Làm Sáng Da", "Skincare"),
    ("SKC002", "Kem Dưỡng Ẩm Ban Đêm", "Skincare"),
    ("SKC003", "Kem Chống Nắng SPF50+ PA+++", "Skincare"),
    ("SKC004", "Nước Hoa Hồng Cân Bằng Da", "Skincare"),
    ("SKC005", "Sữa Rửa Mặt Dịu Nhẹ", "Skincare"),
    ("SKC006", "Kem Dưỡng Mắt Chống Lão Hóa", "Skincare"),
    ("SKC007", "Mặt Nạ Giấy Cấp Ẩm", "Skincare"),
    ("SKC008", "Tẩy Da Chết Hóa Học AHA BHA", "Skincare"),
    ("SKC009", "Essence Dưỡng Da Hàn Quốc", "Skincare"),
    ("SKC010", "Dầu Dưỡng Mặt Squalane", "Skincare"),

    # Body Care (10)
    ("BDC001", "Sữa Dưỡng Thể Trắng Da", "Body Care"),
    ("BDC002", "Gel Tắm Hương Hoa Anh Đào", "Body Care"),
    ("BDC003", "Tẩy Da Chết Body Muối Biển", "Body Care"),
    ("BDC004", "Kem Dưỡng Tay Chống Nứt", "Body Care"),
    ("BDC005", "Kem Gót Chân Mềm Mịn", "Body Care"),
    ("BDC006", "Dầu Dưỡng Thể Khô Nhanh", "Body Care"),
    ("BDC007", "Lăn Khử Mùi 48H", "Body Care"),
    ("BDC008", "Muối Tắm Thư Giãn Lavender", "Body Care"),
    ("BDC009", "Bơ Dưỡng Thể Shea Butter", "Body Care"),
    ("BDC010", "Sữa Tắm Collagen Dưỡng Trắng", "Body Care"),

    # Hair Care (10)
    ("HRC001", "Dầu Gội Phục Hồi Tóc Hư Tổn", "Hair Care"),
    ("HRC002", "Dầu Xả Mềm Mượt Tóc Khô", "Hair Care"),
    ("HRC003", "Ủ Tóc Keratin Chuyên Sâu", "Hair Care"),
    ("HRC004", "Dầu Dưỡng Tóc Argan Oil", "Hair Care"),
    ("HRC005", "Kem Xả Không Xả Dưỡng Ẩm", "Hair Care"),
    ("HRC006", "Dầu Gội Khô Thể Thao", "Hair Care"),
    ("HRC007", "Serum Dưỡng Tóc Bóng Mượt", "Hair Care"),
    ("HRC008", "Tinh Chất Dưỡng Da Đầu", "Hair Care"),
    ("HRC009", "Gôm Xịt Tóc Giữ Nếp 24H", "Hair Care"),
    ("HRC010", "Xịt Dưỡng Tóc Chống Nhiệt", "Hair Care"),

    # Fragrance (10)
    ("FRG001", "Nước Hoa Nữ Floral EDP 50ml", "Fragrance"),
    ("FRG002", "Nước Hoa Nam Woody EDT 100ml", "Fragrance"),
    ("FRG003", "Xịt Thơm Toàn Thân Body Mist", "Fragrance"),
    ("FRG004", "Nước Hoa Unisex Oud EDP 30ml", "Fragrance"),
    ("FRG005", "Nước Hoa Dạng Sáp Solid Perfume", "Fragrance"),
    ("FRG006", "Gel Tắm Hương Nước Hoa Rose", "Fragrance"),
    ("FRG007", "Sữa Dưỡng Thể Hương Nước Hoa", "Fragrance"),
    ("FRG008", "Xịt Thơm Tóc Hair Perfume", "Fragrance"),
    ("FRG009", "Tinh Dầu Khuếch Tán Lavender", "Fragrance"),
    ("FRG010", "Nến Thơm Cao Cấp Vanilla", "Fragrance"),
]

cursor.executemany("INSERT OR REPLACE INTO products VALUES (?,?,?)", products)

for product_id, name, category in products:
    for i in range(60):
        date = datetime.now() - timedelta(days=i)
        qty = random.randint(3, 25)
        cursor.execute(
            "INSERT INTO sales_history VALUES (?,?,?)",
            (product_id, date.strftime("%Y-%m-%d"), qty)
        )

inventory_data = []
for product_id, name, category in products:
    stock = random.randint(20, 200)
    inventory_data.append((product_id, stock))

cursor.executemany("INSERT OR REPLACE INTO inventory VALUES (?,?)", inventory_data)

conn.commit()
conn.close()
print("Done: 50 products added.")
