
from telegram.ext import CommandHandler, ContextTypes, filters, MessageHandler
from telegram import Update, InputFile
from core.database import add_to_buffer, get_buffer_summary, conn, cursor
from core.logic import generate_summary
from core.export import run_export
import os
import shutil

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привіт! Я бот для бюджету. Команди: /add /summary /report_buffer /export")

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        amount = float(context.args[0])
        category = context.args[1]
        description = " ".join(context.args[2:]) if len(context.args) > 2 else "—"
        add_to_buffer(amount, category, description)
        await update.message.reply_text(f"📝 Додано до буфера: {amount} грн | {category} | {description}")
    except:
        await update.message.reply_text("⚠️ Формат: /add 200 Продукти Ашан")

async def summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = generate_summary()
    await update.message.reply_text(result)

async def report_buffer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = get_buffer_summary()
    await update.message.reply_text(result or "Буфер пустий.")

async def export(update: Update, context: ContextTypes.DEFAULT_TYPE):
    path = run_export()
    if path:
        await update.message.reply_document(document=open(path, "rb"))
    else:
        await update.message.reply_text("⚠️ Експорт не вдався.")

async def commit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cursor.execute("INSERT INTO expenses (amount, category, description, date) SELECT amount, category, description, date FROM buffer_expenses")
    cursor.execute("DELETE FROM buffer_expenses")
    conn.commit()
    if os.path.exists("data/media_buffer"):
        os.makedirs("data/media", exist_ok=True)
        for file in os.listdir("data/media_buffer"):
            shutil.move(os.path.join("data/media_buffer", file), os.path.join("data/media", file))
    await update.message.reply_text("✅ Збережено в основну базу.")

async def discard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cursor.execute("DELETE FROM buffer_expenses")
    conn.commit()
    if os.path.exists("data/media_buffer"):
        for file in os.listdir("data/media_buffer"):
            os.remove(os.path.join("data/media_buffer", file))
    await update.message.reply_text("🗑 Буфер очищено.")

def setup_handlers(app):
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add))
    app.add_handler(CommandHandler("summary", summary))
    app.add_handler(CommandHandler("report_buffer", report_buffer))
    app.add_handler(CommandHandler("export", export))
    app.add_handler(CommandHandler("commit", commit))
    app.add_handler(CommandHandler("discard", discard))
