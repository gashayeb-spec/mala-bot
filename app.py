import os
import sqlite3
import requests
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# .env ፋይልን ማንበቢያ
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- DATABASE MODELS ---

# የተጠቃሚዎች መረጃ
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    telegram_id = db.Column(db.String(50), unique=True, nullable=True)
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    balance = db.Column(db.Float, default=0.0)
    is_approved = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)

# የክፍያ ታሪክ
class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    tx_ref = db.Column(db.String(100), unique=True, nullable=False)
    status = db.Column(db.String(20), default='pending') # pending, success, failed
    created_at = db.Column(db.DateTime, server_default=db.func.now())

# ዳታቤዝ መፍጠሪያ
with app.app_context():
    db.create_all()

# --- API ENDPOINTS ---

# 1. አዲስ አባል መመዝገቢያ (Register)
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    phone = data.get('phone')
    
    if User.query.filter_by(phone=phone).first():
        return jsonify({'status': 'error', 'message': 'ይህ ስልክ ቁጥር ቀደም ብሎ ተመዝግቧል!'}), 400

    new_user = User(
        full_name=data.get('full_name'),
        phone=phone,
        telegram_id=data.get('telegram_id')
    )
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'status': 'success', 'message': 'ምዝገባው ተሳክቷል! በአድሚን እስከሚጸድቅ ይጠብቁ።', 'user_id': new_user.id})

# 2. Chapa Payment Initialization (ክፍያ ማስጀመሪያ)
@app.route('/api/pay', methods=['POST'])
def initialize_payment():
    data = request.json
    user_id = data.get('user_id')
    amount = data.get('amount')
    email = data.get('email', 'customer@gmail.com')
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'status': 'error', 'message': 'ተጠቃሚው አልተገኘም'}), 404

    import uuid
    tx_ref = f"MELA-SACCO-{uuid.uuid4().hex[:8]}"

    # Transaction መመዝገብ
    new_tx = Transaction(user_id=user.id, amount=float(amount), tx_ref=tx_ref)
    db.session.add(new_tx)
    db.session.commit()

    # ከ Chapa API ጋር ማያያዝ
    chapa_url = "https://api.chapa.co/v1/transaction/initialize"
    headers = {
        "Authorization": f"Bearer {os.getenv('CHAPA_SECRET_KEY')}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "amount": str(amount),
        "currency": "ETB",
        "email": email,
        "first_name": user.full_name.split()[0],
        "last_name": user.full_name.split()[-1] if len(user.full_name.split()) > 1 else "SACCO",
        "tx_ref": tx_ref,
        "callback_url": f"{request.host_url}api/chapa-webhook",
        "customization[title]": "መላ ሳኮ ቁጠባ",
        "customization[description]": "የወርሀዊ ቁጠባ ክፍያ"
    }

    response = requests.post(chapa_url, json=payload, headers=headers)
    res_data = response.json()

    if res_data.get('status') == 'success':
        return jsonify({
            'status': 'success',
            'checkout_url': res_data['data']['checkout_url'],
            'tx_ref': tx_ref
        })
    else:
        return jsonify({'status': 'error', 'message': 'የክፍያ ሂደቱ አልተሳካም'}), 400

# 3. Chapa Webhook / Verification (ክፍያው መፈጸሙን ማረጋገጫ)
@app.route('/api/verify-payment/<tx_ref>', methods=['GET'])
def verify_payment(tx_ref):
    chapa_url = f"https://api.chapa.co/v1/transaction/verify/{tx_ref}"
    headers = {
        "Authorization": f"Bearer {os.getenv('CHAPA_SECRET_KEY')}"
    }
    
    response = requests.get(chapa_url, headers=headers)
    res_data = response.json()

    if res_data.get('status') == 'success':
        tx = Transaction.query.filter_by(tx_ref=tx_ref).first()
        if tx and tx.status != 'success':
            tx.status = 'success'
            user = User.query.get(tx.user_id)
            user.balance += tx.amount
            db.session.commit()
            
            # ለTelegram Admin ማሳወቂያ መላክ
            send_telegram_notification(f"🔔 **አዲስ ክፍያ ተፈፅሟል!**\n\nተጠቃሚ፡ {user.full_name}\nመጠን፡ {tx.amount} ETB\nTx Ref: {tx_ref}")
            
            return jsonify({'status': 'success', 'message': 'ክፍያው በተሳካ ሁኔታ ተረጋግጧል!'})
            
    return jsonify({'status': 'error', 'message': 'ክፍያው አልተረጋገጠም'}), 400

# Telegram Notification መላኪያ Function
def send_telegram_notification(text):
    bot_token = os.getenv('BOT_TOKEN')
    admin_id = os.getenv('ADMIN_USER_ID')
    if bot_token and admin_id:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {"chat_id": admin_id, "text": text, "parse_mode": "Markdown"}
        try:
            requests.post(url, json=payload)
        except Exception as e:
            print(f"Telegram error: {e}")

# 4. Admin Dashboard API - የአባላት ዝርዝር ማያ
@app.route('/api/admin/users', methods=['GET'])
def get_users():
    users = User.query.all()
    output = []
    for u in users:
        output.append({
            'id': u.id,
            'full_name': u.full_name,
            'phone': u.phone,
            'balance': u.balance,
            'is_approved': u.is_approved
        })
    return jsonify({'users': output})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
