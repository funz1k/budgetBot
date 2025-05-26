from telegram.ext import ApplicationBuilder
from bot.handlers import setup_handlers
from bot.router import setup_conversation, handle_text_buttons

import os
from dotenv import load_dotenv

load_dotenv()
import threading
import http.server
import socketserver

def run_fake_webserver():
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", 8080), handler) as httpd:
        httpd.serve_forever()

threading.Thread(target=run_fake_webserver, daemon=True).start()

TOKEN = os.getenv("BOT_TOKEN")

app = ApplicationBuilder().token(TOKEN).build()
setup_handlers(app)
setup_conversation(app)

if __name__ == '__main__':
    import telegram.error
    try:
            app.run_polling()
    except telegram.error.Conflict:
        print('[❌] Бот вже запущений в іншому місці (getUpdates conflict)')