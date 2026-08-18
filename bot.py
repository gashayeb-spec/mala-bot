import os
import json
import logging
from flask import Flask, request, jsonify, render_template
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Config Variables (እነዚህን በራስዎ Credentials ይተኩ)
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN_HERE")
WEBAPP_URL = os.environ.get("WEBAPP_URL", "https://your-domain-or-ngrok-url.com")
ADMIN_CHAT_ID = os.environ.get("ADMIN_CHAT_ID", "YOUR_ADMIN_TELEGRAM_ID")

# Flask App Initialisation
app = Flask(__name__, template_folder=".", static_folder=".")

# ---------------------------------------------------------
# Telegram Bot Handlers
# ---------------------------------------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/start ሲባል የሚላክ ሰላምታ እና Mini App መክፈቻ ቁልፍ"""
    user = update.effective_user
    first_name = user.first_name if user else "ተጠቃሚ"

    # Telegram Mini App መክፈቻ WebAppInfo ቁልፍ
    keyboard = [
        [
            InlineKeyboardButton(
                "🚀 Mela Bot Mini App ክፈት", 
                web_app=WebAppInfo(url=WEBAPP_URL)
            )
        ],
        [
            InlineKeyboardButton("💬 Official Channel", url="https://t.me/your_channel_username"),
            InlineKeyboardButton("📞 Customer Support", url="https://t.me/your_support_username")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome_text = (
        f"ሰላም {first_name}! 👋\n\n"
        "እንኳን ወደ **Mela Official Bot** በደህና መጡ!\n\n"
        "የእርስዎን አካውንት ለመጠቀም፣ ዲፖዚት ለማድረግ፣ ሎተሪ ለመግዛት እና P2P ለመላክ "
        "ከታች ያለውን **'Mela Bot Mini App ክፈት'** የሚለውን ቁልፍ ይጫኑ።"
    )

    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")

# ---------------------------------------------------------
# Flask Web Server Routes (serves index.html & API)
# ---------------------------------------------------------

@app.route('/')
def index():
    """የ index.html ፋይልን ለ Mini App ያቀርባል"""
    return render_template('index.html')

@app.route('/submit-registration', methods=['POST'])
def submit_registration():
    """ተጠቃሚ ሲመዘገብ መረጃውን ለአድሚን በቴሌግራም ማሳወቂያ ይልካል"""
    data = request.json or {}
    user_id = data.get('telegramId', 'N/A')
    first_name = data.get('firstName', 'N/A')
    father_name = data.get('fatherName', 'N/A')
    phone = data.get('phone', 'N/A')

    logger.info(f"New Registration: {first_name} {father_name} (ID: {user_id}, Phone: {phone})")

    # እዚህ ቦታ ላይ ለአድሚኑ በቴሌግራም ማሳወቅ ወይም Database ውስጥ ማስቀመጥ ይቻላል
    return jsonify({"status": "success", "message": "KYC submitted successfully"}), 200

@app.route('/check-status', methods=['GET'])
def check_status():
    """የተጠቃሚውን የ KYC አፕሩቫል ሁኔታ ይፈትሻል"""
    user_id = request.args.get('user_id')
    # በምሳሌነት አፕሩቭ እንደተደረገ መመለስ (ወደፊት ከ Database ጋር ማያያዝ ይቻላል)
    return jsonify({"status": "approved", "user_id": user_id}), 200

@app.route('/initiate-chapa', methods=['POST'])
def initiate_chapa():
    """ለ Chapa Payment ክፍያ ማስጀመርያ Endpoint"""
    data = request.json or {}
    amount = data.get('amount', 0)
    email = data.get('email', 'user@mela.com')
    
    # የ Chapa Integration Logic እዚህ ላይ ይገባል
    # ምሳሌ Checkout URL:
    checkout_url = f"https://checkout.chapa.co/pay/sample-tx-{amount}"
    
    return jsonify({
        "status": "success",
        "checkout_url": checkout_url
    }), 200

@app.route('/api/notify-admin', methods=['POST'])
def notify_admin():
    """የተጠቃሚ እንቅስቃሴዎችን ለአድሚን መዝገብ ማስተላለፊያ"""
    data = request.json or {}
    details = data.get('details', '')
    user_name = data.get('userName', '')
    
    logger.info(f"[ADMIN NOTIFICATION] {user_name}: {details}")
    return jsonify({"status": "logged"}), 200

# ---------------------------------------------------------
# Main Execution
# ---------------------------------------------------------

def main():
    # Telegram Bot Application
    bot_app = Application.builder().token(BOT_TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))

    print("🤖 Mela Telegram Bot & Flask Server Starting...")
    
    # ማስታወሻ: በምርት (Production) ላይ Flask በ Gunicorn/Uvicorn ይራናል
    app.run(host="0.0.0.0", port=5000, debug=True)

if __name__ == '__main__':
    main()
