import os
import random
import string
import requests
from flask import Flask, render_template, request, jsonify, session, redirect, url_for

app = Flask(__name__)
app.secret_key = "mella_wallet_super_secret_session_key_2026"

TELEGRAM_BOT_TOKEN = "8932085001:AAFSuqyjALyhumCO-Y6RwfHlwz1HJaugevU"
CHAPA_PUBLIC_KEY = "CHAPUBK-hLBEJPiKDlRpfBCqTczyE1OsnrrK3Zhj"
CHASECK_KEY = "CHASECK-SncZN81Mx80yQcPiXJwRXDF6MdgchtNV"

ADMIN_TELEGRAM_ID = "5351353727"

ADMIN_ACCOUNT = {
    "user_id": ADMIN_TELEGRAM_ID,
    "full_name": "System Admin",
    "mella_coins": 1_000_000_000_000,
    "etb_balance": 0.0,
    "usd_balance": 0.0
}

users_db = {}
lottery_tickets = []

EXCHANGE_RATES = {
    "ETB_TO_USD": 0.0083,  
    "USD_TO_ETB": 120.0,
    "ETB_TO_COIN": 10.0,   
    "USD_TO_COIN": 1200.0  
}

def generate_wallet_number():
    digits = ''.join(random.choices(string.digits, k=6))
    return f"MEL-{digits}"

def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Telegram Notification Error: {e}")

# ለአድሚኑ በበተኖች (Inline Buttons) ማሳወቂያ የሚልክ ፋንክሽን
def send_telegram_admin_notification(chat_id, text, user_id):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    reply_markup = {
        "inline_keyboard": [
            [
                {"text": "✅ Approve", "callback_data": f"approve_{user_id}"},
                {"text": "❌ Cancel", "callback_data": f"cancel_{user_id}"},
                {"text": "🚫 Block", "callback_data": f"block_{user_id}"}
            ],
            [
                {"text": "🌐 ወደ Admin Panel ሂድ", "url": "https://mella-bot.onrender.com/admin"}
            ]
        ]
    }
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "reply_markup": reply_markup
    }
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Telegram Notification Error: {e}")

# =========================================================
# ROUTES - USER & SYSTEM
# =========================================================

@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    if str(user_id) == str(ADMIN_TELEGRAM_ID):
        return redirect(url_for('admin_panel'))
        
    user = users_db.get(user_id)
    if not user:
        return redirect(url_for('login'))
        
    return render_template('index.html', user=user, rates=EXCHANGE_RATES)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone = request.form.get('phone')
        password = request.form.get('password')
        
        if phone == "admin" and password == "admin123":
            session['user_id'] = ADMIN_TELEGRAM_ID
            return redirect(url_for('admin_panel'))

        for uid, u in users_db.items():
            if u['phone'] == phone and u['password'] == password:
                if u.get('status') == "Blocked":
                    return render_template('login.html', error="አካውንትዎ ታግዷል! እባክዎን አድሚኑን ያነጋግሩ።")
                session['user_id'] = uid
                return redirect(url_for('home'))
                
        return render_template('login.html', error="የተሳሳተ ስልክ ቁጥር ወይም ፓስወርድ!")
        
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        phone = request.form.get('phone')
        national_id = request.form.get('national_id')
        password = request.form.get('password')
        telegram_id = request.form.get('telegram_id')

        if not (full_name and phone and national_id and password and telegram_id):
            return jsonify({"status": "error", "message": "እባክዎን ሁሉንም መስኮች ይሙሉ!"}), 400

        clean_phone = phone.replace(" ", "").replace("-", "")
        if len(clean_phone) == 10 and (clean_phone.startswith("09") or clean_phone.startswith("07")):
            formatted_phone = "+251" + clean_phone[1:]
        elif len(clean_phone) == 13 and clean_phone.startswith("+251"):
            formatted_phone = clean_phone
        else:
            return jsonify({"status": "error", "message": "እባክዎን ትክክለኛ የኢትዮጵያ ስልክ ቁጥር ያስገቡ!"}), 400

        WELCOME_BONUS = 100
        if ADMIN_ACCOUNT["mella_coins"] >= WELCOME_BONUS:
            ADMIN_ACCOUNT["mella_coins"] -= WELCOME_BONUS

        wallet_num = generate_wallet_number()
        user_key = str(telegram_id).strip()
        
        new_user = {
            "user_id": user_key,
            "full_name": full_name,
            "phone": formatted_phone,
            "national_id": national_id,
            "password": password,
            "wallet_number": wallet_num,
            "status": "Pending",
            "etb_balance": 0.0,
            "usd_balance": 0.0,
            "mella_coins": WELCOME_BONUS
        }

        users_db[user_key] = new_user

        # ለአድሚን በቴሌግራም የሚላክ ማሳወቂያ በInline Buttons
        admin_msg = (
            f"<b>🚨 አዲስ የዋሌት ምዝገባ ጥያቄ!</b>\n\n"
            f"<b>👤 ስም:</b> {full_name}\n"
            f"<b>📞 ስልክ:</b> {formatted_phone}\n"
            f"<b>🪪 National ID:</b> {national_id}\n"
            f"<b>🆔 Telegram ID:</b> <code>{telegram_id}</code>\n"
            f"<b>💳 የዋሌት ቁጥር:</b> <code>{wallet_num}</code>\n"
            f"<b>🎁 ቦነስ:</b> 100 Coins\n\n"
            f"👇 <b>እባክዎን ከታች እርምጃ ይውሰዱ፦</b>"
        )
        send_telegram_admin_notification(ADMIN_TELEGRAM_ID, admin_msg, user_key)

        return jsonify({"status": "success", "message": "ምዝገባው ተሳክቷል! የአድሚን ማረጋገጫ በመጠበቅ ላይ ይገኛል።"})

    return render_template('register.html')

# =========================================================
# TELEGRAM WEBHOOK (በተኖቹን ሲጫኑ ምላሽ የሚሰጥበት)
# =========================================================
@app.route('/telegram_webhook', methods=['POST'])
def telegram_webhook():
    data = request.get_json()
    
    if data and "callback_query" in data:
        callback = data["callback_query"]
        callback_id = callback["id"]
        action_data = callback["data"]
        
        try:
            action, user_id = action_data.split("_")
            user = users_db.get(user_id)

            if user:
                if action == "approve":
                    user['status'] = "Approved"
                    response_text = f"✅ {user['full_name']} ጸድቋል!"
                    send_telegram_message(user_id, "🎉 **እንኳን ደስ አለዎት!** የ Mella Wallet አካውንትዎ በትክክል ጽድቋል::")
                elif action == "cancel":
                    user['status'] = "Cancelled"
                    response_text = f"❌ {user['full_name']} ተሰርዟል!"
                    send_telegram_message(user_id, "⚠️ የ Mella Wallet ምዝገባ ጥያቄዎ ውድቅ ተደርጓል።")
                elif action == "block":
                    user['status'] = "Blocked"
                    response_text = f"🚫 {user['full_name']} ታግዷል!"
                    send_telegram_message(user_id, "🚫 አካውንትዎ በአድሚኑ ታግዷል።")
            else:
                response_text = "⚠️ ተጠቃሚው በዳታቤዝ ውስጥ አልተገኘም!"

            answer_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/answerCallbackQuery"
            requests.post(answer_url, json={"callback_query_id": callback_id, "text": response_text, "show_alert": True})
        except Exception as e:
            print(f"Webhook Callback Error: {e}")

    return jsonify({"status": "success"}), 200

# =========================================================
# ADMIN ROUTE
# =========================================================
@app.route('/admin')
def admin_panel():
    return render_template('admin.html', users=users_db, admin=ADMIN_ACCOUNT, tickets=lottery_tickets)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
