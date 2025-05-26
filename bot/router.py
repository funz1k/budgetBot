
from telegram.ext import ConversationHandler, MessageHandler, filters, ContextTypes
from telegram import Update
from core.database import add_to_buffer

AWAITING_EXPENSE_INPUT = 1

async def start_expense_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Введи витрату у форматі:
*Сума Категорія Опис (необов’язково)*
Наприклад: `200 Продукти Ашан`",
        parse_mode="Markdown"
    )
    return AWAITING_EXPENSE_INPUT

async def process_expense_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        parts = update.message.text.strip().split()
        amount = float(parts[0])
        category = parts[1]
        description = " ".join(parts[2:]) if len(parts) > 2 else "—"
        add_to_buffer(amount, category, description)
        await update.message.reply_text(f"✅ Додано до буфера: {amount} грн | {category} | {description}")
    except:
        await update.message.reply_text("⚠️ Формат невірний. Спробуй ще раз: `200 Продукти Ашан`", parse_mode="Markdown")
        return AWAITING_EXPENSE_INPUT
    return ConversationHandler.END

async def cancel_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Скасовано.")
    return ConversationHandler.END

def setup_conversation(app):
    app.add_handler(
        ConversationHandler(
            entry_points=[MessageHandler(filters.Regex("(?i)^\+?\s?додати.*"), start_expense_input)],
            states={
                AWAITING_EXPENSE_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_expense_input)]
            },
            fallbacks=[MessageHandler(filters.Regex("(?i)^скасувати$"), cancel_input)],
        )
    )
