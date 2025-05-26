from bot.handlers import setup_handlers
from telegram.ext import ApplicationBuilder
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

app = ApplicationBuilder().token(TOKEN).build()
setup_handlers(app)

if __name__ == '__main__':
    app.run_polling()
