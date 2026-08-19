import os
import random
import string
import requests
from flask import Flask, render_template, request, jsonify, session, redirect, url_for

app = Flask(__name__)
app.secret_key = "mella_wallet_super_secret_session_key_2026"

# =========================================================
# የሰጠኸኝ ቁልፎች (INTEGRATED KEYS)
# =========================================================
TELEGRAM_BOT_TOKEN = "8932085001:AAFSuqyjALyhumCO-Y6RwfHlwz1HJaugevU"
CHAPA_PUBLIC_KEY = "CHAPUBK-hLBEJPiKDlRpfBCqTczyE1OsnrrK3Zhj"
CHAPA_SECRET_KEY = "CHASECK-SncZN81Mx80yQcPiXJwRXDF6MdgchtNV"

ADMIN_TELEGRAM_ID = "5351353727"  # ያንተ የቴሌግራም ID

# =========================================================
# DATABASE (In-Memory Data Storage)
# =========================================================
# የአድሚን 1 ትሪሊየን Mella Coin ካዝና
ADMIN_ACCOUNT = {
    "user_id": ADMIN_TELEGRAM_ID,
    "full_name": "System Admin",
    "mella_coins": 1_000_000_000_000, # 1 Trillion Mella Coins
    "etb_balance": 0.0,
    "usd_balance": 0.0
}

users_db = {}
lottery_tickets = []

EXCHANGE_RATES = {
    "ETB_TO_USD": 0.0083,  
    "USD_TO_ETB": 120.0,
    "ETB_TO_COIN": 10.0,   # 1 ETB = 10 Mella Coins
    "USD_TO_COIN": 1200.0  
}

# =========================================================
# HELPER FUNCTIONS
# =========================================================
def generate_wallet_number():
    digits = ''.join(random.choices(string.digits, k=6))
    return f"MEL-{digits}"

def send_telegram_message(chat_id, text):
    """በቦቱ በኩል ለተጠቃሚው ወይም ለአድሚኑ ማሳወቂያ መላኪያ"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    try:
        response = requests.post(url, json=payload, timeout=5)
        return response.json()
    except Exception as e:
        print(f"Telegram Notification Error: {e}")
        return None

# =========================================================
# ROUTES - USERS
# =========================================================
@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    user = users_db.get(user_id)
    if not user:
        return redirect(url_for('login'))
        
    return render_template('index.html', user=user, rates=EXCHANGE_RATES)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone = request.form.get('phone')
        password = request.form.get('password')
        
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

        # የስልክ ቁጥር ዲጂት ቼክ ማድረጊያ (09, 07 ወይም +251)
        clean_phone = phone.replace(" ", "").replace("-", "")
        if len(clean_phone) == 10 and (clean_phone.startswith("09") or clean_phone.startswith("07")):
            formatted_phone = "+251" + clean_phone[1:]
        elif len(clean_phone) == 13 and clean_phone.startswith("+251"):
            formatted_phone = clean_phone
        else:
            return jsonify({"status": "error", "message": "እባክዎን ትክክለኛ የኢትዮጵያ ስልክ ቁጥር ያስገቡ!"}), 400

        # 100 Mella Coin ከአድሚኑ አካውንት ተቀንሶ ለአዲሱ ተመዝጋቢ ይሰጣል
        WELCOME_BONUS = 100
        if ADMIN_ACCOUNT["mella_coins"] >= WELCOME_BONUS:
            ADMIN_ACCOUNT["mella_coins"] -= WELCOME_BONUS
        else:
            WELCOME_BONUS = 0

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

        # ለአድሚን በቴሌግራም መልእክት ይላካል
        admin_msg = (
            f"<b>🚨 አዲስ የዋሌት ምዝገባ!</b>\n\n"
            f"<b>ስም:</b> {full_name}\n"
            f"<b>ስልክ:</b> {formatted_phone}\n"
            f"<b>National ID:</b> {national_id}\n"
            f"<b>የዋሌት ቁጥር:</b> {wallet_num}\n"
            f"<b>የተሰጠ ነጻ ቦነስ:</b> 100 Coins\n\n"
            f"እባክዎን ከአድሚን ፓናል ገብተው ያረጋግጡ (Confirm/Block)።"
        )
        send_telegram_message(ADMIN_TELEGRAM_ID, admin_msg)

        return jsonify({"status": "success", "message": "ምዝገባው ተሳክቷል! 100 የመላ ኮይን ተጨምሮልዎታል።"})

    return render_template('register.html')

# =========================================================
# CHAPA PAYMENT PROCESS
# =========================================================
@app.route('/deposit/chapa', methods=['POST'])
def init_chapa_payment():
    data = request.json
    user_id = session.get('user_id')
    amount = data.get('amount')
    
    if not user_id or not amount:
        return jsonify({"error": "የተሳሳተ ጥያቄ"}), 400

    user = users_db.get(user_id)
    tx_ref = f"tx-mella-{random.randint(100000, 999999)}"

    headers = {
        'Authorization': f'Bearer {CHAPA_SECRET_KEY}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        "amount": str(amount),
        "currency": "ETB",
        "email": f"user_{user_id}@mellawallet.com",
        "first_name": user['full_name'].split()[0],
        "last_name": "User",
        "tx_ref": tx_ref,
        "callback_url": f"https://yourdomain.com/chapa/callback/{tx_ref}",
        "customization": {
            "title": "Mella Wallet Deposit",
            "description": "ገንዘብ ወደ ሜላ ዋሌት ማስገቢያ"
        }
    }

    try:
        response = requests.post("https://api.chapa.co/v1/transaction/initialize", json=payload, headers=headers)
        res_data = response.json()

        if res_data.get("status") == "success":
            user['etb_balance'] += float(amount) # Demo auto-credit
            return jsonify({"status": "success", "checkout_url": res_data['data']['checkout_url']})
        else:
            return jsonify({"status": "error", "message": res_data.get("message", "የክፍያ ስህተት")}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# =========================================================
# COIN EXCHANGE & LOTTERY SYSTEM
# =========================================================
@app.route('/exchange/coin', methods=['POST'])
def exchange_to_coin():
    user_id = session.get('user_id')
    user = users_db.get(user_id)
    data = request.json
    
    from_currency = data.get('from_currency')
    amount = float(data.get('amount', 0))

    if from_currency == "ETB":
        if user['etb_balance'] < amount:
            return jsonify({"error": "በቂ የኢትዮጵያ ብር የለዎትም!"}), 400
        coins_gained = amount * EXCHANGE_RATES['ETB_TO_COIN']
        user['etb_balance'] -= amount
        user['mella_coins'] += coins_gained

    return jsonify({"status": "success", "new_coins": user['mella_coins']})

@app.route('/lottery/buy', methods=['POST'])
def buy_lottery():
    user_id = session.get('user_id')
    user = users_db.get(user_id)
    data = request.json
    ticket_count = int(data.get('tickets', 1))
    cost_per_ticket = 50 
    
    total_cost = ticket_count * cost_per_ticket

    if user['mella_coins'] < total_cost:
        return jsonify({"error": "ሎተሪ ለመቁረጥ በቂ Mella Coin የለዎትም!"}), 400

    # ኮይኑ ቀጥታ ወደ አድሚኑ ገቢ ይሆናል
    user['mella_coins'] -= total_cost
    ADMIN_ACCOUNT['mella_coins'] += total_cost

    ticket_numbers = []
    for _ in range(ticket_count):
        t_num = f"LOT-{random.randint(1000, 9999)}"
        ticket_numbers.append(t_num)
        lottery_tickets.append({
            "user_id": user_id,
            "user_name": user['full_name'],
            "ticket_number": t_num
        })

    return jsonify({"status": "success", "tickets": ticket_numbers, "remaining_coins": user['mella_coins']})

# =========================================================
# ADMIN CONTROLS
# =========================================================
@app.route('/admin')
def admin_panel():
    return render_template('admin.html', users=users_db, admin=ADMIN_ACCOUNT, tickets=lottery_tickets)

@app.route('/admin/action', methods=['POST'])
def admin_action():
    data = request.json
    target_user_id = data.get('user_id')
    action = data.get('action') 
    
    user = users_db.get(target_user_id)
    if user:
        user['status'] = action.capitalize()
        send_telegram_message(target_user_id, f"የእርስዎ ዋሌት ሁኔታ ወደ '{action}' ተቀይሯል።")
        return jsonify({"status": "success"})
    return jsonify({"error": "ተጠቃሚ አልተገኘም"}), 404

@app.route('/admin/broadcast', methods=['POST'])
def admin_broadcast():
    data = request.json
    target_group = data.get('target') 
    message = data.get('message')
    winner_id = data.get('winner_id')

    if target_group == 'all':
        for uid in users_db:
            send_telegram_message(uid, f"<b>📢 ከአድሚን የተላከ ማስታወቂያ:</b>\n\n{message}")
    elif target_group == 'lottery_buyers':
        buyers = set([t['user_id'] for t in lottery_tickets])
        for uid in buyers:
            send_telegram_message(uid, f"<b>🎯 የሎተሪ ማሳወቂያ:</b>\n\n{message}")
    elif target_group == 'winner_only' and winner_id:
        send_telegram_message(winner_id, f"<b>🎉 እንኳን ደስ አለዎት! የአሸናፊነት ማሳወቂያ:</b>\n\n{message}")

    return jsonify({"status": "success", "message": "መልእክቱ ተልኳል!"})

@app.route('/admin/deposit-coin', methods=['POST'])
def admin_deposit_coin():
    data = request.json
    target_id = data.get('user_id')
    amount = float(data.get('amount', 0))

    user = users_db.get(target_id)
    if user and ADMIN_ACCOUNT['mella_coins'] >= amount:
        ADMIN_ACCOUNT['mella_coins'] -= amount
        user['mella_coins'] += amount
        send_telegram_message(target_id, f"<b>🎁 ሽልማት:</b> አድሚኑ {amount} Mella Coin ገቢ አድርጎልዎታል!")
        return jsonify({"status": "success", "new_balance": user['mella_coins']})
    return jsonify({"error": "ስህተት ተፈጥሯል"}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
