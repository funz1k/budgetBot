
from telegram.ext import ConversationHandler, MessageHandler, filters, ContextTypes
from telegram import Update
from core.database import add_to_buffer
from bot.handlers import summary, report_buffer, export, commit, discard

AWAITING_EXPENSE_INPUT = 1

async def start_expense_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        """Введи витрату у форматі:
Сума Категорія Опис (необов’язково)
Наприклад: 200 Продукти Ашан""",
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
        await update.message.reply_text(
            "⚠️ Формат невірний. Спробуй ще раз: 200 Продукти Ашан",
            parse_mode="Markdown"
        )
        return AWAITING_EXPENSE_INPUT
    return ConversationHandler.END

async def cancel_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Скасовано.")
    return ConversationHandler.END

# Универсальный обработчик текстовых кнопок
async def handle_text_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    if "звіт" in text:
        await summary(update, context)
    elif "експорт" in text or "выгруз" in text:
        await export(update, context)
    elif "буфер" in text:
        await report_buffer(update, context)
    elif "зберегти" in text or "commit" in text:
        await commit(update, context)
    elif "очистити" in text or "discard" in text:
        await discard(update, context)
    elif "скасувати" in text:
        await cancel_input(update, context)

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
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_buttons))
