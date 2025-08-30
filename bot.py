import os
import re
import html
import requests
from flask import Flask, request

TOKEN = os.environ.get("TELEGRAM_TOKEN")
app = Flask(__name__)

# --- HTML Template with Theme + Video Player + Credit ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Notes</title>
  <style>
    body {{
      font-family: Arial, sans-serif;
      margin: 0;
      padding: 0;
      background: var(--bg);
      color: var(--text);
      transition: background 0.3s, color 0.3s;
    }}
    :root {{
      --bg: #ffffff;
      --text: #000000;
      --box-bg: #f1f1f1;
    }}
    .dark {{
      --bg: #181818;
      --text: #ffffff;
      --box-bg: #242424;
    }}
    .container {{
      max-width: 900px;
      margin: auto;
      padding: 20px;
    }}
    h2 {{
      text-align: center;
      margin-bottom: 20px;
    }}
    .subject-box {{
      border-radius: 12px;
      padding: 15px;
      margin-bottom: 15px;
      background: var(--box-bg);
    }}
    .subject-title {{
      font-size: 20px;
      margin-bottom: 10px;
      font-weight: bold;
    }}
    .video-player {{
      width: 100%;
      max-width: 720px;
      height: 400px;
      margin: 20px auto;
      display: block;
    }}
    .toggle-btn {{
      margin: 10px;
      padding: 10px 20px;
      border: none;
      border-radius: 8px;
      cursor: pointer;
      background: #007bff;
      color: white;
    }}
    .credit {{
      margin-top: 40px;
      text-align: center;
      font-size: 14px;
      opacity: 0.8;
    }}
  </style>
  <script>
    function toggleTheme(){{
      document.body.classList.toggle('dark');
    }}
    function play(link){{
      const p = document.getElementById('player');
      p.src = link;
      p.play();
      window.scrollTo({{ top:0, behavior:'smooth' }});
    }}
  </script>
</head>
<body>
  <div class="container">
    <button class="toggle-btn" onclick="toggleTheme()">🌞/🌙 Theme</button>
    <h2>My Notes</h2>
    {content}
    <video id="player" class="video-player" controls></video>
    <div class="credit">Made by Antaryami 🇮🇳</div>
  </div>
</body>
</html>
"""

def txt_to_html(text):
    lines = text.splitlines()
    html_parts = []
    current_subject = None
    buffer = []

    def flush_subject():
        nonlocal buffer, current_subject
        if current_subject and buffer:
            html_parts.append(f"""
            <div class="subject-box">
              <div class="subject-title">{html.escape(current_subject)}</div>
              <div>{"<br>".join(buffer)}</div>
            </div>""")
        buffer = []

    for line in lines:
        line = line.strip()
        if not line:
            continue
        subject_match = re.match(r"#\s*(.+)", line)
        if subject_match:
            flush_subject()
            current_subject = subject_match.group(1)
        else:
            # अगर link है तो play() function call होगा
            if re.match(r"^https?://", line):
                buffer.append(f'<a href="#" onclick="play(\'{line}\');return false;">{line}</a>')
            else:
                buffer.append(html.escape(line))
    flush_subject()

    return HTML_TEMPLATE.format(content="\n".join(html_parts))

# --- Telegram Handlers ---
def send_html(chat_id, html_content):
    filename = "notes.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)

    url = f"https://api.telegram.org/bot{TOKEN}/sendDocument"
    with open(filename, "rb") as f:
        requests.post(url, data={"chat_id": chat_id}, files={"document": f})

@app.route(f"/webhook/{TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()
    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"]["text"]
        html_content = txt_to_html(text)
        send_html(chat_id, html_content)
    return {"ok": True}

@app.route("/")
def home():
    return "Bot is running ✅"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
