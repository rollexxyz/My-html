import os
import asyncio
from flask import Flask, request
from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ======================
# 🔑 Config
TOKEN = "8221949574:AAFx-XYEwyXwZKsKqoNUeffn0q51908HCc0"
APP_URL = "https://my-html-bd10.onrender.com"
PORT = int(os.environ.get("PORT", 8080))
# ======================

app = Flask(__name__)

# Global asyncio loop
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

# Telegram bot (webhook mode)
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

    # ==========================
    # HTML Template
    # ==========================
    html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Generated Subject Page</title>
  <style>
    body { margin:0; font-family:"Inter",sans-serif; background:#f5f7fa; color:#222; }
    .credit {background:#fde047;color:#111;font-weight:900;text-align:center;padding:8px;font-size:16px;}
    .header { background:#111827;color:#fff;text-align:center;padding:20px; }
    .title { font-size:24px;font-weight:800; }
    .subheading { font-size:16px;color:#fde047;font-weight:900; margin-top:6px; }
    .tabs{display:flex;justify-content:center;gap:10px;margin:16px;}
    .tab{padding:10px 20px;background:#fff;border-radius:8px;cursor:pointer;font-weight:700}
    .tab.active{background:#0ea5e9;color:#fff}
    .content{display:none;max-width:1000px;margin:12px auto;padding:0 16px}
    .content.active{display:block}
    .card{background:#fff;padding:16px;border-radius:10px;box-shadow:0 2px 6px rgba(0,0,0,.1);margin-top:10px;}
    .section-title{margin:0 0 10px;font-weight:800;color:#0b83ba}
    .list{display:grid;gap:6px}
    .item{background:#f3f6fb;padding:10px;border-radius:8px}
    .item a{text-decoration:none;color:#0ea5e9;font-weight:bold}
    .item:hover{background:#0ea5e9;}
    .item:hover a{color:#fff}
  </style>
</head>
<body>
  <div class="credit">MADE BY ANTARYAMI</div>
  <header class="header">
    <div class="title">Subject Spl. (Theory + Pract.)</div>
    <div class="subheading">🙏 JAY BAJRANGBALI 🙏</div>
  </header>

  <nav class="tabs">
    <div class="tab active" data-target="videos">Videos</div>
    <div class="tab" data-target="pdfs">PDFs</div>
    <div class="tab" data-target="others">Others</div>
  </nav>
"""

    # PDFs
    html += '<div id="pdfs" class="content"><div class="card"><h2 class="section-title">All PDFs</h2><div class="list">'
    for t, u in pdfs:
        html += f'<div class="item"><a href="{u}" target="_blank">{t}</a></div>'
    html += "</div></div></div>"

    # Videos
    html += '<div id="videos" class="content active"><div class="card"><h2 class="section-title">All Videos</h2><div class="list">'
    for t, u in videos:
        html += f'<div class="item"><a href="{u}" target="_blank">{t}</a></div>'
    html += "</div></div></div>"

    # Others
    html += '<div id="others" class="content"><div class="card"><h2 class="section-title">Other Resources</h2><div class="list">'
    for t, u in others:
        html += f'<div class="item"><a href="{u}" target="_blank">{t}</a></div>'
    html += "</div></div></div>"

    # Tabs JS
    html += """
<script>
document.querySelectorAll(".tab").forEach(tab=>{
  tab.onclick=()=>{
    document.querySelectorAll(".tab").forEach(t=>t.classList.remove("active"));
    tab.classList.add("active");
    document.querySelectorAll(".content").forEach(c=>c.classList.remove("active"));
    document.getElementById(tab.dataset.target).classList.add("active");
  };
});
</script>
</body>
</html>"""

    with open("output.html", "w", encoding="utf-8") as f:
        f.write(html)

    await update.message.reply_document(InputFile("output.html"))


# Handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.Document.FileExtension("txt"), handle_file))


@app.route("/")
def home():
    return "Bot is running with webhook!"


@app.route(f"/webhook/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    # Queue me daal dete hain
    application.update_queue.put_nowait(update)
    return "ok"


if __name__ == "__main__":
    # Start dispatcher
    loop.run_until_complete(application.initialize())
    loop.run_until_complete(application.start())

    # Webhook set
    application.bot.set_webhook(url=f"{APP_URL}/webhook/{TOKEN}")
    app.run(host="0.0.0.0", port=PORT)
