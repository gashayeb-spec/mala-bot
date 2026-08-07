import os
import requests
from flask import Flask, render_template, request, jsonify, redirect
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

app = Flask(__name__)

# ከምስሉ የተወሰዱ መረጃዎች
TELEGRAM_TOKEN = "8543715567:AAFPG7v8h-YJchs6aCYZ_Tad_35-iELISLw"
ADMIN_CHAT_ID = "5351353727"
CHAPA_SECRET_KEY = "CHASECK-SncZN81Mx80yQcPiXJwRXF6MdgentNV"

# የተጠቃሚዎች መረጃ ጊዜያዊ ማከማቻ (Database ፋንታ)
users_db = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register_user():
    data = request.json
    telegram_id = data.get('telegram_id')
    
    # የተጠቃሚ መረጃዎችን መቀበል (ስም፣ ስልክ፣ ኢሜይል፣ መታወቂያ እና 2FA)
    users_db[telegram_id] = {
        "full_name": data.get('full_name'),
        "phone": data.get('phone'),
        "email": data.get('email'),
        "id_document": data.get('id_document'),
        "two_fa": data.get('two_fa'),
        "balance_etb": 0.0,
        "balance_usdt": 0.0
    }
    return jsonify({"status": "success", "message": "ኪስ ቦርሳዎ በተሳካ ሁኔታ ተከፍቷል!"})

@app.route('/pay/chapa', methods=['POST'])
def initialize_chapa():
    data = request.json
    amount = data.get('amount')
    email = data.get('email')
    first_name = data.get('first_name')
    
    url = "https://api.chapa.co/v1/transaction/initialize"
    headers = {
        "Authorization": f"Bearer {CHAPA_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "amount": str(amount),
        "currency": "ETB",
        "email": email,
        "first_name": first_name,
        "tx_ref": f"tx-{os.urandom(4).hex()}",
        "callback_url": "https://yourdomain.com/verify-payment"
    }
    
    response = requests.post(url, json=payload, headers=headers)
    return jsonify(response.json())

# የቴሌግራም ቦት ትዕዛዝ (Start)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("🌐 ዋሌት ለመክፈት (App ይክፈቱ)", web_app={"url": "https://yourdomain.com"})],
        [InlineKeyboardButton("💰 ቀሪ ሂሳብ ለማየት", callback_data="balance")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"ሰላም {user.first_name}! ወደ ዲጂታል ኪስ ቦርሳዎ በደህና መጡ። ከታች ያለውን በመጫን አካውንትዎትን ይክፈቱ:",
        reply_markup=reply_markup
    )

def run_telegram_bot():
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.run_polling()

if __name__ == '__main__':
    # ቦቱን እና ዌብ ሰርቨርን በአንድላይ ማስኬድ ይቻላል
    app.run(host='0.0.0.0', port=5000)
