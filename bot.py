import os
import requests
from flask import Flask, request

TOKEN = os.environ.get("TELEGRAM_TOKEN", "YOUR_BOT_TOKEN")
app = Flask(__name__)

# ---------------- HTML Generator (Same UI + Play Button) ---------------- #
def txt_to_html(text: str) -> str:
    subjects = []
    current_subject = None
    lines = text.splitlines()

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if line.startswith("# "):  # Subject heading
            current_subject = {"title": line[2:], "items": []}
            subjects.append(current_subject)
        else:
            if current_subject is None:
                current_subject = {"title": "General", "items": []}
                subjects.append(current_subject)
            current_subject["items"].append(line)

    html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Notes</title>
  <style>
    body { font-family: 'Segoe UI', sans-serif; background:#f0f2f5; }
    .container { max-width: 1000px; margin:auto; padding:20px; }
    h1 { text-align:center; margin-bottom:30px; color:#333; }
    .subject-box {
      background:#fff; border-radius:12px; padding:20px; margin-bottom:20px;
      box-shadow:0 4px 10px rgba(0,0,0,0.1);
    }
    .subject-title { font-size:22px; font-weight:bold; margin-bottom:15px; color:#007bff; }
    .item { margin-left:20px; margin-bottom:10px; font-size:16px; }
    .item button {
      background:none; border:none; color:#e63946; font-size:16px; cursor:pointer;
      text-align:left; padding:0;
    }
    .item button:hover { text-decoration:underline; }
    .player { width:100%; max-width:720px; margin:20px auto; display:block; }
    video { width:100%; border-radius:10px; }
    .credit { margin-top:40px; text-align:center; font-size:14px; color:#555; opacity:0.8; }
  </style>
  <script>
    function play(link){
        const p = document.getElementById('player');
        p.src = link;
        p.play();
        window.scrollTo({ top:0, behavior:'smooth' });
    }
  </script>
</head>
<body>
  <div class="container">
    <h1>📘 My Notes</h1>
    <video id="player" class="player" controls></video>
"""

    for subject in subjects:
        html += f"<div class='subject-box'>"
        html += f"<div class='subject-title'>{subject['title']}</div>"
        for item in subject["items"]:
            if item.startswith("http"):
                # 👇 Button banaya (new tab nahi khulega, direct play hoga)
                html += f"<div class='item'><button onclick=\"play('{item}')\">▶️ {item}</button></div>"
            else:
                html += f"<div class='item'>{item}</div>"
        html += "</div>"

    html += """
    <div class="credit">Made by Antaryami 🇮🇳</div>
  </div>
</body>
</html>
"""
    return html

# ---------------- Send HTML back to Telegram ---------------- #
def send_html(chat_id, html_content):
    url = f"https://api.telegram.org/bot{TOKEN}/sendDocument"
    files = {"document": ("notes.html", html_content, "text/html")}
    data = {"chat_id": chat_id, "caption": "✅ HTML file generated\nMade by Antaryami 🇮🇳"}
    requests.post(url, data=data, files=files)

# ---------------- Webhook ---------------- #
@app.route(f"/webhook/{TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]

        # Case 1: Plain text input
        if "text" in data["message"]:
            text = data["message"]["text"]
            html_content = txt_to_html(text)
            send_html(chat_id, html_content)

        # Case 2: TXT file input
        elif "document" in data["message"]:
            file_id = data["message"]["document"]["file_id"]

            # Get file path from Telegram
            file_info = requests.get(f"https://api.telegram.org/bot{TOKEN}/getFile?file_id={file_id}").json()
            file_path = file_info["result"]["file_path"]

            # Download file
            file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_path}"
            txt_data = requests.get(file_url).text

            # Convert & send back
            html_content = txt_to_html(txt_data)
            send_html(chat_id, html_content)

    return {"ok": True}

# ---------------- Root Route ---------------- #
@app.route("/")
def home():
    return "Bot is running ✅"

# ---------------- Local Run ---------------- #
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
