import os
import asyncio
from flask import Flask, request
from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8221949574:AAFx-XYEwyXwZKsKqoNUeffn0q51908HCc0"
APP_URL = "https://my-html-bd10.onrender.com"
PORT = int(os.environ.get("PORT", 8080))

app = Flask(__name__)

application = Application.builder().token(TOKEN).updater(None).build()

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Send me a TXT file (format: TYPE|Title|URL)")

# Handle TXT
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    doc = update.message.document
    if not doc.file_name.endswith(".txt"):
        await update.message.reply_text("❌ Please send a TXT file only.")
        return

    file = await doc.get_file()
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

    html = "<html><body><h1>Generated Links</h1>"
    if pdfs:
        html += "<h2>PDFs</h2><ul>" + "".join([f'<li><a href="{u}">{t}</a></li>' for t,u in pdfs]) + "</ul>"
    if videos:
        html += "<h2>Videos</h2><ul>" + "".join([f'<li><a href="{u}">{t}</a></li>' for t,u in videos]) + "</ul>"
    if others:
        html += "<h2>Others</h2><ul>" + "".join([f'<li><a href="{u}">{t}</a></li>' for t,u in others]) + "</ul>"
    html += "</body></html>"

    with open("output.html", "w", encoding="utf-8") as f:
        f.write(html)

    await update.message.reply_document(InputFile("output.html"))

# Handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.Document.ALL, handle_file))   # ✅ FIXED

@app.route("/")
def home():
    return "Bot running!"

@app.route(f"/webhook/{TOKEN}", methods=["POST"])
async def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return "ok"

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(application.initialize())
    asyncio.get_event_loop().run_until_complete(application.start())
    application.bot.set_webhook(url=f"{APP_URL}/webhook/{TOKEN}")
    app.run(host="0.0.0.0", port=PORT)
