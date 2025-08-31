import os
import asyncio
from flask import Flask, request
from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ======================
# Config
TOKEN = "8221949574:AAFx-XYEwyXwZKsKqoNUeffn0q51908HCc0"
APP_URL = "https://my-html-bd10.onrender.com"
PORT = int(os.environ.get("PORT", 8080))
# ======================

app = Flask(__name__)

# Telegram bot (no polling, only webhook)
application = Application.builder().token(TOKEN).updater(None).build()


# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Send me a TXT file with links (format: TYPE|Title|URL) and I will generate styled HTML page!"
    )


# Handle TXT file
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.document.get_file()
    txt_content = await file.download_as_bytearray()
    txt_content = txt_content.decode("utf-8")

    videos, pdfs, others = [], [], []
    for line in txt_content.splitlines():
        if not line.strip():
            continue
        try:
            type_, title, url = line.split("|")
            if type_.upper() == "VIDEO":
                videos.append((title.strip(), url.strip()))
            elif type_.upper() == "PDF":
                pdfs.append((title.strip(), url.strip()))
            else:
                others.append((title.strip(), url.strip()))
        except:
            continue

    html = """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Generated Page</title></head><body>
<h1>Generated Subject Page</h1>
"""

    if pdfs:
        html += "<h2>PDFs</h2><ul>"
        for t, u in pdfs:
            html += f'<li><a href="{u}" target="_blank">{t}</a></li>'
        html += "</ul>"

    if videos:
        html += "<h2>Videos</h2><ul>"
        for t, u in videos:
            html += f'<li><a href="{u}" target="_blank">{t}</a></li>'
        html += "</ul>"

    if others:
        html += "<h2>Others</h2><ul>"
        for t, u in others:
            html += f'<li><a href="{u}" target="_blank">{t}</a></li>'
        html += "</ul>"

    html += "</body></html>"

    with open("output.html", "w", encoding="utf-8") as f:
        f.write(html)

    await update.message.reply_document(InputFile("output.html"))


# Add handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.Document.FileExtension("txt"), handle_file))


@app.route("/")
def home():
    return "Bot is running with webhook!"


@app.route(f"/webhook/{TOKEN}", methods=["POST"])
async def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, application.bot)
    await application.process_update(update)   # ✅ This processes the update
    return "ok"


if __name__ == "__main__":
    # Initialize bot
    asyncio.get_event_loop().run_until_complete(application.initialize())
    asyncio.get_event_loop().run_until_complete(application.start())

    # Set webhook
    application.bot.set_webhook(url=f"{APP_URL}/webhook/{TOKEN}")
    app.run(host="0.0.0.0", port=PORT)
