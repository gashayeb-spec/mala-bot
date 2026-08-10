import os
import asyncio
import threading
from flask import Flask, render_template, request, jsonify
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
import requests

load_dotenv()

# ኮንፊግሬሽን
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAPA_SECRET_KEY = os.getenv("CHAPA_SECRET_KEY")
# Render ላይ የተሰጠዎትን የዌብሳይት ሊንክ እዚህ ያስገቡ
WEB_APP_URL = "https://mela-bot--site.onrender.com" 

# 1. የ Flask ክፍል
app = Flask(__name__, template_folder='.')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/pay', methods=['POST'])
def pay():
    data = request.json
    amount = data.get('amount')
    email = data.get('email', 'user@mela.com')
    
    headers = {
        "Authorization": f"Bearer {CHAPA_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "amount": str(amount),
        "currency": "ETB",
        "email": email,
        "first_name": "Mela",
        "last_name": "User",
        "tx_ref": "mela-tx-" + os.urandom(4).hex(),
        "callback_url": WEB_APP_URL + "/callback",
        "return_url": "https://t.me/your_bot_username"
    }
    
    response = requests.post("https://api.chapa.co/v1/transaction/initialize", json=payload, headers=headers)
    return jsonify(response.json())

# 2. የቴሌግራም ቦት ክፍል
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 መተግበሪያውን ክፈት", web_app=WebAppInfo(url=WEB_APP_URL))]
    ])
    await message.answer("እንኳን ወደ ማላ በደህና መጡ! መተግበሪያውን ለመጠቀም ከታች ያለውን ቁልፍ ይጫኑ፦", reply_markup=kb)

async def run_bot():
    await dp.start_polling(bot)

def start_telegram_bot():
    asyncio.run(run_bot())

if __name__ == '__main__':
    # ቦቱን በተለየ Thread እንዲሰራ ማድረግ
    bot_thread = threading.Thread(target=start_telegram_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # Flask ሰርቨሩን ማስጀመር
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
