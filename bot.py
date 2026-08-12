import logging
import requests
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio
from flask import Flask, render_template, request, jsonify
import threading
import json

# -- የተጠቃሚው ትክክለኛ መረጃዎች --
BOT_TOKEN = "8543715567:AAEeL0HgHcw62LhGaj3tNn9yJp2bh5XdmfM"
ADMIN_CHAT_ID = "5351353727" 
CHAPA_PUBLIC_KEY = "CHAPUBK-hLBEJPiKDlRpfBCqTczyE1OsnrrK3Zhj"
CHAPA_SECRET_KEY = "CHASECK-SncZN81Mx80yQcPiXJwRXDF6MdgchtNV"

# -- ከ Render ያገኙት ትክክለኛ የዌብሳይት ሊንክ --
WEB_APP_URL = "https://mela-bot.onrender.com"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# -- Flask ሰርቨር --
app = Flask(__name__, template_folder='.')

@app.route('/')
def home():
    return render_template('index.html')

# -- የቻፓ (Chapa) ክፍያ ሊንክ ማመንጫ ኤፒአይ (API) --
@app.route('/initiate-chapa', methods=['POST'])
def initiate_chapa():
    req_data = request.json
    amount = req_data.get('amount')
    email = req_data.get('email', 'user@mela.com')
    first_name = req_data.get('first_name', 'Mela')
    last_name = req_data.get('last_name', 'User')
    phone = req_data.get('phone', '0911000000')
    
    tx_ref = f"mela-tx-{asyncio.get_event_loop().time()}"
    
    headers = {
        "Authorization": f"Bearer {CHAPA_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "amount": str(amount),
        "currency": "ETB",
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "phone_number": phone,
        "tx_ref": tx_ref,
        "callback_url": f"{WEB_APP_URL}/chapa-callback",
        "return_url": WEB_APP_URL
    }
    
    response = requests.post("https://api.chapa.co/v1/transaction/initialize", json=payload, headers=headers)
    res_data = response.json()
    
    if res_data.get('status') == 'success':
        return jsonify({"status": "success", "checkout_url": res_data['data']['checkout_url']})
    else:
        return jsonify({"status": "error", "message": "የክፍያ ሊንክ መፍጠር አልተቻለም"})

def run_web():
    app.run(host="0.0.0.0", port=10000)

# ዌብ ሰርቨሩን በጀርባ ማስጀመር
threading.Thread(target=run_web, daemon=True).start()

# /start ትዕዛዝ ሲሰጥ
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    welcome_text = (
        "<b>እንኳን ወደ መላ.ቦት (Mela-bot) በደህና መጡ!</b>\n\n"
        "ደህንነቱ የተጠበቀ ዋሌት ለመክፈት፣ ኬዋይሲ (KYC) ለማረጋገጥ "
        "እና የገንዘብ ዝውውር ለማድረግ ከታች ያለውን ቁልፍ ይጫኑ።"
    )
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🚀 ዋሌት ክፈት & ኬዋይሲ አድርግ", 
                    web_app=WebAppInfo(url=WEB_APP_URL)
                )
            ]
        ]
    )
    
    await message.answer(welcome_text, reply_markup=keyboard, parse_mode="HTML")

# ከዌብ አፕ (HTML) የሚላኩ መረጃዎችን መቀበያ እና ለአድሚን ማረጋገጫ መላኪያ
@dp.message(F.web_app_data)
async def handle_web_app_data(message: types.Message):
    data_json = message.web_app_data.data
    user_id = message.from_user.id
    
    await message.answer("መረጃዎ እና የኬዋይሲ ሰነድዎ ለአድሚን ተልኳል! እባክዎ ሲረጋገጥ ይጠብቁ።")
    
    if ADMIN_CHAT_ID:
        try:
            parsed = json.loads(data_json)
            info_text = f"ስም: {parsed.get('firstName')} {parsed.get('fatherName')}\nስልክ: {parsed.get('phoneNumber')}\nኢሜይል: {parsed.get('email')}\nሀገር: {parsed.get('country')}"
        except:
            info_text = data_json

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ አጽድቅ (Approve Wallet)", callback_data=f"approve_{user_id}")]
        ])
        
        admin_text = f"🔔 <b>አዲስ የኬዋይሲ/ምዝገባ ጥያቄ መጥቷል!</b>\n\nተጠቃሚ: @{message.from_user.username}\n{info_text}"
        await bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_text, reply_markup=keyboard, parse_mode="HTML")

# አድሚኑ አጽድቅ (Approve) ሲጫን
@dp.callback_query(F.data.startswith("approve_"))
async def approve_user(callback: types.CallbackQuery):
    target_user_id = callback.data.split("_")[1]
    
    try:
        await bot.send_message(
            chat_id=target_user_id, 
            text="🎉 <b>እንኳን ደስ አለዎት!</b>\n\nየእርስዎ ኬዋይሲ (KYC) በአድሚን ጸድቋል። አሁን ዋሌትዎ ክፍት ነው፤ በቻፓ በኩል ገንዘብ ማስገባት እና መገበያየት ይችላሉ!", 
            parse_mode="HTML"
        )
        await callback.message.edit_text(callback.message.text + "\n\n<b>[✅ ጸድቋል]</b>", parse_mode="HTML")
        await callback.answer("ተጠቃሚው በተሳካ ሁኔታ ጸድቋል!")
    except Exception as e:
        await callback.answer(f"ስህተት ተፈጥሯል: {e}", show_alert=True)

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
