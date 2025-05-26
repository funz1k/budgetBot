
import sqlite3
import os
import zipfile
from datetime import datetime

def run_export():
    archive_name = f"data/budget_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    try:
        conn = sqlite3.connect("data/budget.db", check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("SELECT amount, category, description, date FROM expenses")
        rows = cursor.fetchall()
        with open("data/expenses.csv", "w", encoding="utf-8") as f:
            f.write("amount,category,description,date\n")
            for r in rows:
                f.write(f"{r[0]},{r[1]},{r[2]},{r[3]}\n")
        with zipfile.ZipFile(archive_name, "w") as zipf:
            zipf.write("data/expenses.csv", arcname="expenses.csv")
            if os.path.exists("data/media"):
                for root, _, files in os.walk("data/media"):
                    for file in files:
                        path = os.path.join(root, file)
                        arcname = os.path.relpath(path, "data")
                        zipf.write(path, arcname)
        os.remove("data/expenses.csv")
        return archive_name
    except:
        return None
