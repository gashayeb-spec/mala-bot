import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ሚስጥራዊ ቁልፎች (እዚህ አገልጋይ ላይ ብቻ ይመደባሉ)
CHAPA_SECRET_KEY = "CHASECK-SncZN81Mx80yQcPiXJwRXDF6MdgchtNV"
BOT_TOKEN = "8932085001:AAFSuqyjALyhumCO-Y6RwfHlwz1HJaugevU"
ADMIN_CHAT_ID = "5351353727"

# 1. ለአስተዳዳሪው በቴሌግራም የማረጋገጫ መልእክት መላኪያ Endpoint
@app.route('/api/notify-admin', methods=['POST'])
def notify_admin():
    data = request.json
    msg = (
        f"🔔 *አዲስ የኪስ ቦርሳ (Wallet) ምዝገባ ጥያቄ!*\n\n"
        f"👤 *ስም:* {data.get('firstName')} {data.get('fatherName')}\n"
        f"📞 *ስልክ:* {data.get('phone')}\n"
        f"🆔 *መታወቂያ ቁጥር:* {data.get('nationalId')}\n"
        f"✉️ *ኢሜል:* {data.get('email')}\n"
        f"🔹 *Telegram ID:* `{data.get('telegramId')}`\n\n"
        f"እባክዎን ወደ Admin Panel በመግባት አካውንቱን ያጽድቁ!"
    )
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": ADMIN_CHAT_ID,
        "text": msg,
        "parse_mode": "Markdown"
    }
    
    try:
        res = requests.post(url, json=payload)
        return jsonify({"success": True, "data": res.json()}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# 2. የ Chapa Deposit ክፍያ መጀመርያ Endpoint
@app.route('/api/chapa/initialize', methods=['POST'])
def initialize_chapa():
    data = request.json
    amount = data.get('amount')
    email = data.get('email', 'user@melabot.com')
    first_name = data.get('firstName', 'User')
    phone = data.get('phone', '')
    
    import uuid
    tx_ref = f"mela-tx-{uuid.uuid4().hex[:8]}"

    headers = {
        "Authorization": f"Bearer {CHAPA_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "amount": str(amount),
        "currency": "ETB",
        "email": email,
        "first_name": first_name,
        "phone_number": phone,
        "tx_ref": tx_ref,
        "callback_url": "https://yourdomain.com/api/chapa/callback",
        "customization": {
            "title": "Mela Wallet Deposit",
            "description": "ሒሳብ መሙያ (Deposit)"
        }
    }

    try:
        response = requests.post("https://api.chapa.co/v1/transaction/initialize", json=payload, headers=headers)
        res_data = response.json()
        if res_data.get("status") == "success":
            return jsonify({"status": "success", "checkout_url": res_data["data"]["checkout_url"]}), 200
        else:
            return jsonify({"status": "failed", "message": res_data.get("message")}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
