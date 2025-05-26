
import sqlite3
import os

# Гарантируем наличие папки для базы
os.makedirs("data", exist_ok=True)

conn = sqlite3.connect("data/budget.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount REAL,
    category TEXT,
    description TEXT,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS buffer_expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount REAL,
    category TEXT,
    description TEXT,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)""")
conn.commit()

def add_to_buffer(amount, category, description):
    cursor.execute("INSERT INTO buffer_expenses (amount, category, description) VALUES (?, ?, ?)", (amount, category, description))
    conn.commit()

def get_buffer_summary():
    cursor.execute("SELECT category, SUM(amount) FROM buffer_expenses GROUP BY category")
    rows = cursor.fetchall()
    if not rows:
        return None
    return "\n".join([f"{cat}: {round(total, 2)} грн" for cat, total in rows])

def commit_buffer():
    with open("data/main.txt", "a", encoding="utf-8") as f:
        for item in buffer:
            f.write(f"{item}\n")
    buffer.clear()

def discard_buffer():
    buffer.clear()

def export_to_csv():
    import csv, os
    os.makedirs("data", exist_ok=True)
    with open("data/export.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Amount", "Category", "Description"])
        for item in buffer:
            writer.writerow(item)
    return "data/export.csv"
