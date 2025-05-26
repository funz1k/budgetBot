import logging
import sqlite3
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

conn = sqlite3.connect("budget.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount REAL,
    category TEXT,
    description TEXT,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)""")
conn.commit()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я бот для отслеживания бюджета.\nДобавь трату: /add 200 Продукты Ашан\nОтчёт: /report\nСводка: /summary\nНовый месяц: /reset")

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        amount = float(context.args[0])
        category = context.args[1]
        description = " ".join(context.args[2:])
        cursor.execute("INSERT INTO expenses (amount, category, description) VALUES (?, ?, ?)", (amount, category, description))
        conn.commit()
        await update.message.reply_text(f"✅ Добавлено: {amount} грн | {category} | {description}")
    except Exception as e:
        await update.message.reply_text("Ошибка при добавлении. Формат: /add 200 Продукты Ашан")

async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cursor.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
    rows = cursor.fetchall()
    if not rows:
        await update.message.reply_text("Расходов пока нет.")
        return
    text = "\n".join([f"{row[0]}: {round(row[1], 2)} грн" for row in rows])
    await update.message.reply_text("📊 Расходы по категориям:\n" + text)

async def summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    benchmarks = {
        "Жильё": 17000,
        "Продукты": 9468,
        "Стики": 8100,
        "Кафе": 6312,
        "Транспорт": 3156
    }
    cursor.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
    rows = cursor.fetchall()
    text = ""
    for cat, benchmark in benchmarks.items():
        total = sum(row[1] for row in rows if cat.lower() in row[0].lower())
        delta = total - benchmark
        text += f"{cat}: {round(total, 2)} / {benchmark} грн (Δ {round(delta, 2)})\n"
    await update.message.reply_text("📉 Сравнение с эталоном:\n" + text)

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cursor.execute("DELETE FROM expenses")
    conn.commit()
    await update.message.reply_text("🗑 Расходы сброшены. Новый месяц начался.")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("add", add))
app.add_handler(CommandHandler("report", report))
app.add_handler(CommandHandler("summary", summary))
app.add_handler(CommandHandler("reset", reset))

if __name__ == '__main__':
    app.run_polling()