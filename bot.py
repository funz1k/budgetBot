# Основной бот с буфером, кнопками и автоэкспортом
import logging
import sqlite3
import os
import datetime
import zipfile
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from telegram import Update, InputFile, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

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
cursor.execute("""CREATE TABLE IF NOT EXISTS buffer_expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount REAL,
    category TEXT,
    description TEXT,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)""")
conn.commit()

user_keyboard = ReplyKeyboardMarkup([
    ["➕ Добавить трату", "📊 Сводка дня"],
    ["🧾 Чеки / медиа", "📤 Выгрузить"],
    ["📑 Помощь", "⚙ Настройки"]
], resize_keyboard=True)

admin_keyboard = ReplyKeyboardMarkup([
    ["✅ Сохранить (commit)", "🗑 Очистить буфер"],
    ["📂 Показать буфер", "🔁 Сброс / новый день"]
], resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Добро пожаловать в финансовый бот!", reply_markup=user_keyboard)

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        amount = float(context.args[0])
        category = context.args[1]
        description = " ".join(context.args[2:])
        cursor.execute("INSERT INTO buffer_expenses (amount, category, description) VALUES (?, ?, ?)", (amount, category, description))
        conn.commit()
        await update.message.reply_text(f"📝 Буфер: {amount} грн | {category} | {description}")
    except:
        await update.message.reply_text("Ошибка. Пример: /add 200 Продукты Ашан")

async def report_buffer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cursor.execute("SELECT category, SUM(amount) FROM buffer_expenses GROUP BY category")
    rows = cursor.fetchall()
    if not rows:
        await update.message.reply_text("Буфер пуст.")
        return
    text = "\n".join([f"{row[0]}: {round(row[1], 2)} грн" for row in rows])
    await update.message.reply_text("📊 Буфер расходов:\n" + text)

async def commit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cursor.execute("INSERT INTO expenses (amount, category, description, date) SELECT amount, category, description, date FROM buffer_expenses")
    cursor.execute("DELETE FROM buffer_expenses")
    conn.commit()
    if os.path.exists("media_buffer"):
        os.makedirs("media", exist_ok=True)
        for file in os.listdir("media_buffer"):
            os.rename(os.path.join("media_buffer", file), os.path.join("media", file))
    await update.message.reply_text("✅ Буфер сохранён в базу.")

async def discard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cursor.execute("DELETE FROM buffer_expenses")
    conn.commit()
    if os.path.exists("media_buffer"):
        for file in os.listdir("media_buffer"):
            os.remove(os.path.join("media_buffer", file))
    await update.message.reply_text("🗑 Буфер очищен.")

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

async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    path = "media_buffer"
    os.makedirs(path, exist_ok=True)
    file_id = None
    if update.message.photo:
        file_id = update.message.photo[-1].file_id
    elif update.message.document:
        file_id = update.message.document.file_id
    elif update.message.voice:
        file_id = update.message.voice.file_id
    else:
        return
    file = await context.bot.get_file(file_id)
    now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    ext = file.file_path.split('.')[-1]
    filename = f"{path}/media_{now}.{ext}"
    await file.download_to_drive(filename)
    await update.message.reply_text("🧾 Чек или файл сохранён во временный буфер")

async def export(update: Update = None, context: ContextTypes.DEFAULT_TYPE = None):
    archive_name = "budget_export.zip"
    cursor.execute("SELECT amount, category, description, date FROM expenses")
    rows = cursor.fetchall()
    with open("expenses.csv", "w", encoding="utf-8") as f:
        f.write("amount,category,description,date\n")
        for r in rows:
            f.write(f"{r[0]},{r[1]},{r[2]},{r[3]}\n")
    with zipfile.ZipFile(archive_name, 'w') as zipf:
        zipf.write("expenses.csv")
        if os.path.exists("media"):
            for root, _, files in os.walk("media"):
                for file in files:
                    path = os.path.join(root, file)
                    zipf.write(path)
    os.remove("expenses.csv")
    if os.path.exists("media"):
        for file in os.listdir("media"):
            os.remove(os.path.join("media", file))
    if update:
        await update.message.reply_document(InputFile(archive_name))
    os.remove(archive_name)

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📋 Главное меню:", reply_markup=user_keyboard)

async def menu_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🛠 Техническое меню:", reply_markup=admin_keyboard)

app = ApplicationBuilder().token(TOKEN).build()

# Планировщик ежедневной выгрузки
scheduler = BackgroundScheduler()
scheduler.add_job(lambda: app.create_task(export()), 'cron', hour=23, minute=59)
scheduler.start()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("add", add))
app.add_handler(CommandHandler("report_buffer", report_buffer))
app.add_handler(CommandHandler("commit", commit))
app.add_handler(CommandHandler("discard", discard))
app.add_handler(CommandHandler("summary", summary))
app.add_handler(CommandHandler("export", export))
app.add_handler(CommandHandler("menu", menu))
app.add_handler(CommandHandler("menu_admin", menu_admin))
app.add_handler(MessageHandler(filters.PHOTO | filters.Document.ALL | filters.VOICE, handle_media))

if __name__ == '__main__':
    app.run_polling()
