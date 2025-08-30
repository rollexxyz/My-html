import os
import requests
from flask import Flask, request, Response
def txt_to_html(text: str) -> str:
    subjects = []
    current_subject = None
    lines = text.splitlines()

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if line.startswith("# "):  # Heading as subject
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
    body { font-family: Arial, sans-serif; padding: 20px; }
    video { width: 100%; max-height: 400px; border-radius: 10px; margin-bottom:20px; }
    .subject-box { padding: 12px; margin: 12px 0; border-radius: 10px; background: #f5f5f5; }
    .subject-title { font-size: 18px; font-weight: bold; margin-bottom: 10px; }
    .item { margin-left: 20px; margin-bottom: 6px; }
    .credit { margin-top:20px; text-align:center; font-size:14px; opacity:0.7; }
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
  <h2>📺 Video Player</h2>
  <video id="player" controls></video>
"""

    # Subject wise box
    for subject in subjects:
        html += f"<div class='subject-box'>"
        html += f"<div class='subject-title'>{subject['title']}</div>"
        for item in subject["items"]:
            if item.startswith("http"):
                html += f"<div class='item'><a href='#' onclick=\"play('{item}')\">▶️ {item}</a></div>"
            else:
                html += f"<div class='item'>{item}</div>"
        html += "</div>"

    html += """
  <div class="credit">Made by Antaryami 🇮🇳</div>
</body>
</html>
"""
    return html
TOKEN = os.environ.get("TELEGRAM_TOKEN") or "8221949574:AAFx-XYEwyXwZKsKqoNUeffn0q51908HCc0"
app = Flask(__name__)

# --- TXT → HTML Converter ---
def txt_to_html(text: str) -> str:
    subjects = []
    current_subject = None
    lines = text.splitlines()

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if line.startswith("# "):  # Heading as subject
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
    body {
      font-family: Arial, sans-serif;
      padding: 20px;
      transition: background 0.3s, color 0.3s;
    }
    body.light { background: #ffffff; color: #000000; }
    body.dark { background: #121212; color: #ffffff; }

    .toggle-btn {
      padding: 8px 16px;
      border-radius: 10px;
      border: none;
      cursor: pointer;
      margin-bottom: 20px;
    }

    .subject-box {
      border-radius: 12px;
      padding: 15px;
      margin-bottom: 20px;
      box-shadow: 0 2px 6px rgba(0,0,0,0.2);
    }
    .subject-title {
      font-size: 20px;
      font-weight: bold;
      margin-bottom: 10px;
    }
    .item {
      margin-left: 20px;
      margin-bottom: 8px;
    }

    .credit {
      margin-top: 30px;
      font-size: 14px;
      text-align: center;
      opacity: 0.7;
    }

    video {
      width: 100%;
      max-height: 400px;
      margin-top: 10px;
      border-radius: 10px;
    }
  </style>
</head>
<body class="light">
  <button class="toggle-btn" onclick="toggleTheme()">🌗 Toggle Theme</button>
"""

    # Subject wise box
    colors = ["#f8d7da", "#d4edda", "#d1ecf1", "#fff3cd", "#e2e3e5"]
    for idx, subject in enumerate(subjects):
        color = colors[idx % len(colors)]
        html += f"<div class='subject-box' style='background:{color}'>"
        html += f"<div class='subject-title'>{subject['title']}</div>"
        for item in subject["items"]:
            if item.startswith("http"):
                # Video link
                if item.endswith((".mp4", ".m3u8")):
                    html += f"<div class='item'><video controls src='{item}'></video></div>"
                else:
                    html += f"<div class='item'><a href='{item}' target='_blank'>{item}</a></div>"
            else:
                html += f"<div class='item'>{item}</div>"
        html += "</div>"

    html += """
  <div class="credit">Made by Antaryami 🇮🇳</div>

  <script>
    function toggleTheme(){
      document.body.classList.toggle('dark');
      document.body.classList.toggle('light');
    }
  </script>
</body>
</html>
"""
    return html

# --- Send HTML back to Telegram ---
def send_html(chat_id, html_content):
    with open("output.html", "w", encoding="utf-8") as f:
        f.write(html_content)

    url = f"https://api.telegram.org/bot{TOKEN}/sendDocument"
    files = {"document": open("output.html", "rb")}
    data = {"chat_id": chat_id, "caption": "✅ Here is your HTML file\nMade by Antaryami 🇮🇳"}
    requests.post(url, files=files, data=data)

# --- Webhook ---
@app.route(f"/webhook/{TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]

        # --- Case 1: Normal text ---
        if "text" in data["message"]:
            text = data["message"]["text"]
            html_content = txt_to_html(text)
            send_html(chat_id, html_content)

        # --- Case 2: TXT file upload ---
        elif "document" in data["message"]:
            file_id = data["message"]["document"]["file_id"]

            # Get file path from Telegram
            file_info = requests.get(f"https://api.telegram.org/bot{TOKEN}/getFile?file_id={file_id}").json()
            file_path = file_info["result"]["file_path"]

            # Download the file
            file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_path}"
            txt_data = requests.get(file_url).text

            # Convert to HTML and send back
            html_content = txt_to_html(txt_data)
            send_html(chat_id, html_content)

    return {"ok": True}

@app.route("/")
def home():
    return "Bot is running ✅"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
