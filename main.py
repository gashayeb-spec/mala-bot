import os
import logging
import requests
from flask import Flask, request, jsonify, render_template_string

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Credentials & Config provided
BOT_TOKEN = "8543715567:AAFPG7v8h-YJchs6aCYZ_Tad_35-iELISLw"
ADMIN_CHAT_ID = "5351353727"
CHAPA_SECRET_KEY = "CHASECK-SncZN81Mx80yQcPiXJwRXDF6MdgehtNV"
SUPPORT_PHONE = "0916039015"
MPESA_NAME = "ጋሻዬ በጅጉ ሄሬጉ"

TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# In-memory mock database for users, wallet balances, and pins
users_db = {
    5351353727: {
        "user_id": 5351353727,
        "username": "Koket_X",
        "full_name": "Gashaye Bejigu",
        "wallet_balance": 0.0,
        "wallet_pin": None
    }
}

@app.route("/")
def index():
    # Reads and renders index.html from the same directory
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        return render_template_string(html_content, support_phone=SUPPORT_PHONE, mpesa_name=MPESA_NAME)
    except FileNotFoundError:
        return "index.html file not found in the repository!", 404

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    if data and "message" in data:
        chat_id = data["message"]["chat"]["id"]
        user_name = data["message"]["from"].get("first_name", "User")
        text = data["message"].get("text", "")

        if text == "/start":
            reply_text = (
                f"ሰላም {user_name}! እንኳን ወደ ጠቃሚ Bot በደህና መጡ።\n\n"
                f"📞 የደንበኛ ድጋፍ / Telebirr / CBE: {SUPPORT_PHONE}\n"
                f"👤 M-Pesa ስም: {MPESA_NAME}"
            )
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
                "chat_id": chat_id,
                "text": reply_text
            })
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
