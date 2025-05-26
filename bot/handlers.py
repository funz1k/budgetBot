
from telegram.ext import CommandHandler, MessageHandler, ContextTypes, filters
from telegram import Update
from core.logic import generate_summary
from core.database import add_to_buffer, get_buffer_summary
from core.export import run_export

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привіт! Я бот для обліку бюджету. Введи /add <сума> <категорія> <опис>")

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

def setup_handlers(app):
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add))
    app.add_handler(CommandHandler("summary", summary))
    app.add_handler(CommandHandler("report_buffer", report_buffer))
    app.add_handler(CommandHandler("export", export))
