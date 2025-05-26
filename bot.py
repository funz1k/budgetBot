from telegram.ext import ApplicationBuilder
from bot.handlers import setup_handlers
from bot.router import setup_conversation
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

app = ApplicationBuilder().token(TOKEN).build()
setup_handlers(app)
setup_conversation(app)

if __name__ == '__main__':
    app.run_polling()
