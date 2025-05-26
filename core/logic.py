
import sqlite3

def generate_summary():
    benchmarks = {
        "Жильё": 17000,
        "Продукты": 9468,
        "Стики": 8100,
        "Кафе": 6312,
        "Транспорт": 3156
    }
    conn = sqlite3.connect("data/budget.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
    rows = cursor.fetchall()
    result = ""
    for cat, benchmark in benchmarks.items():
        total = sum(row[1] for row in rows if cat.lower() in row[0].lower())
        delta = total - benchmark
        result += f"{cat}: {round(total, 2)} / {benchmark} грн (Δ {round(delta, 2)})\n"
    return result
