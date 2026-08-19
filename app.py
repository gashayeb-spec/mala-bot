import os
import random
import string
import requests
from flask import Flask, render_template, request, jsonify, session, redirect, url_for

app = Flask(__name__)
app.secret_key = "mella_wallet_super_secret_session_key_2026"

TELEGRAM_BOT_TOKEN = "8932085001:AAFSuqyjALyhumCO-Y6RwfHlwz1HJaugevU"
CHAPA_PUBLIC_KEY = "CHAPUBK-hLBEJPiKDlRpfBCqTczyE1OsnrrK3Zhj"
CHAPA_SECRET_KEY = "CHASECK-SncZN81Mx80yQcPiXJwRXDF6MdgchtNV"

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

# =========================================================
# ROUTES - USER & SYSTEM
# =========================================================

@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    user = users_db.get(user_id)
    if not user and user_id != ADMIN_TELEGRAM_ID:
        return redirect(url_for('login'))
        
    return render_template('index.html', user=user, rates=EXCHANGE_RATES)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone = request.form.get('phone')
        password = request.form.get('password')
        
        # ለአድሚን መግቢያ
        if phone == "admin" and password == "admin123":
            session['user_id'] = ADMIN_TELEGRAM_ID
            return redirect(url_for('admin_panel'))

        for uid, u in users_db.items():
            if u['phone'] == phone and u['password'] == password:
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
        user_key = telegram_id or str(random.randint(100000, 999999))
        
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

        # በቴሌግራም ለአድሚን የሚላክ ማሳወቂያ
        admin_msg = (
            f"<b>🚨 አዲስ የዋሌት ምዝገባ!</b>\n\n"
            f"<b>ስም:</b> {full_name}\n"
            f"<b>ስልክ:</b> {formatted_phone}\n"
            f"<b>National ID:</b> {national_id}\n"
            f"<b>የዋሌት ቁጥር:</b> {wallet_num}\n"
            f"<b>የተሰጠ ነጻ ቦነስ:</b> 100 Coins\n\n"
            f"👇 ማረጋገጫ ለመስጠት አድሚን ፓናል ይግቡ፦\n"
            f"https://mella-bot.onrender.com/admin"
        )
        send_telegram_message(ADMIN_TELEGRAM_ID, admin_msg)

        return jsonify({"status": "success", "message": "ምዝገባው ተሳክቷል!"})

    return render_template('register.html')

# =========================================================
# ADMIN ROUTE (አንድ ጊዜ ብቻ የተጻፈው ትክክለኛው ክፍል)
# =========================================================
@app.route('/admin')
def admin_panel():
    return render_template('admin.html', users=users_db, admin=ADMIN_ACCOUNT, tickets=lottery_tickets)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
