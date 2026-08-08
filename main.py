import os
import requests
from flask import Flask, request

app = Flask(__name__)

TOKEN = "8543715567:AAFPG7v8h-YJchs6aCYZ_Tad_35-iELISLw"
ADMIN_CHAT_ID = "5351353727"
TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}"

@app.route(f"/{TOKEN}", methods=["POST"])
def telegram_webhook():
    update = request.get_json()
    
    # 1. ተጠቃሚው መልዕክት ወይም ትዕዛዝ ሲልክ (ለምሳሌ /start)
    if "message" in update:
        message = update["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "")
        
        if text == "/start":
            welcome_msg = (
                "እንኳን ወደ **ጋሻዬ ሀዋሳ የእቁብ ማስተዳደሪያ ቦት** በደህና መጡ! 🤝\n\n"
                "ይህ ቦት የእቁብ ቁጥሮችን ለመያዝ፣ ክፍያዎችን ለመፈጸም እና ደህንነቱ የተጠበቀ አሰራርን ለመከተል የተዘጋጀ ነው።\n\n"
                "እባክዎ ከታች ያሉትን መመሪያዎች በመከተል እቁብዎን ይመዝገቡ!"
            )
            requests.post(f"{TELEGRAM_API}/sendMessage", json={
                "chat_id": chat_id,
                "text": welcome_msg,
                "parse_mode": "Markdown"
            })

    # 2. አድሚኑ የማረጋገጫ አዝራሮችን (Inline Buttons) ሲጫን
    elif "callback_query" in update:
        callback = update["callback_query"]
        data = callback["data"]
        chat_id = callback["message"]["chat"]["id"]
        message_id = callback["message"]["message_id"]
        
        if data.startswith("approve_"):
            ticket_no = data.split("_")[1]
            requests.post(f"{TELEGRAM_API}/editMessageText", json={
                "chat_id": chat_id,
                "message_id": message_id,
                "text": f"✅ እቁብ ቁጥር {ticket_no} ተረጋግጦ ተመዝግቧል!"
            })
            requests.post(f"{TELEGRAM_API}/answerCallbackQuery", json={
                "callback_query_id": callback["id"],
                "text": "በተሳካ ሁኔታ ጸድቋል!"
            })
            
        elif data.startswith("reject_"):
            ticket_no = data.split("_")[1]
            requests.post(f"{TELEGRAM_API}/editMessageText", json={
                "chat_id": chat_id,
                "message_id": message_id,
                "text": f"❌ እቁብ ቁጥር {ticket_no} ውድቅ ተደርጓል።"
            })
            requests.post(f"{TELEGRAM_API}/answerCallbackQuery", json={
                "callback_query_id": callback["id"],
                "text": "ውድቅ ተደርጓል!"
            })

    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
