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

# የተመዝጋቢዎች መረጃ ማከማቻ
registered_users = set()

# -- Flask ሰርቨር --
app = Flask(__name__, template_folder='.')

@app.route('/')
def home():
    return render_template('index.html')

# -- ከዌብሳይት በቀጥታ የሚመጣ የምዝገባ መረጃ መቀበያ ኤፒአይ --
@app.route('/submit-registration', methods=['POST'])
def submit_registration():
    try:
        data = request.json
        first_name = data.get('firstName', '')
        father_name = data.get('fatherName', '')
        grand_father_name = data.get('grandFatherName', '')
        mother_name = data.get('motherName', '')
        phone = data.get('phoneNumber', '')
        
        info_text = (
            f"👤 <b>አዲስ የዌብ ምዝገባ/ኬዋይሲ ጥያቄ!</b>\n\n"
            f"• ስም: <b>{first_name} {father_name} {grand_father_name}</b>\n"
            f"• የእናት ስም: {mother_name}\n"
            f"• ስልክ ቁጥር: {phone}"
        )
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ አጽድቅ (Approve Wallet)", callback_data="approve_web_user")]
        ])
        
        loop.run_until_complete(bot.send_message(
            chat_id=ADMIN_CHAT_ID, 
            text=info_text, 
            reply_markup=keyboard, 
            parse_mode="HTML"
        ))
        
        return jsonify({"status": "success", "message": "መረጃው ለአድሚን በተሳካ ሁኔታ ተልኳል"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# -- የቻፓ (Chapa) ክፍያ ሊንክ ማመንጫ ኤፒአይ --
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

threading.Thread(target=run_web, daemon=True).start()

# /start ትዕዛዝ
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    registered_users.add(message.from_user.id)
    
    welcome_text = (
        "🌟 <b>እንኳን ወደ መላ.ቦት (Mela-bot) በደህና መጡ!</b> 🌟\n\n"
        "💰 <b>ደህንነቱ የተጠበቀ የዲጂታል ዋሌት እና የገንዘብ ዝውውር መድረክ።</b>\n\n"
        "📌 <i>ምን ማድረግ ይችላሉ?</i>\n"
        "• ፈጣን እና ደህንነቱ የተጠበቀ የዋሌት አካውንት ይክፈቱ።\n"
        "• መታወቂያዎን በመጫን ኬዋይሲ (KYC) ያረጋግጡ።\n"
        "• በቻፓ (Chapa) በመጠቀም በብር (ETB) ገንዘብ ያስገቡ እና ያውጡ።\n"
        "• መላ ኮይን እና ዩኤስዲቲ (USDT) ይቀይሩ እንዲሁም ሎተሪ ይሳተፉ!\n\n"
        "👇 እባክዎ ከታች ያለውን ማስታወቂያ አንብበው ሲጨርሱ ለመጀመር ቁልፉን ይጫኑ።"
    )
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🚀 ስታርት - ዋሌት ክፈት & ኬዋይሲ አድርግ", 
                    web_app=WebAppInfo(url=WEB_APP_URL)
                )
            ]
        ]
    )
    
    await message.answer(welcome_text, reply_markup=keyboard, parse_mode="HTML")

# -- የአድሚን ስታቲስቲክስ ትዕዛዝ (/stats) --
@dp.message(Command("stats"))
async def admin_stats(message: types.Message):
    if str(message.from_user.id) == str(ADMIN_CHAT_ID):
        total_users = len(registered_users)
        await message.answer(f"📊 <b>የቦቱ ስታቲስቲክስ</b>\n\n👥 አጠቃላይ ተጠቃሚዎች ብዛት: <b>{total_users}</b>", parse_mode="HTML")
    else:
        await message.answer("ይህንን ትዕዛዝ ለመጠቀም ፈቃድ የለዎትም።")

# -- የአድሚን ማስታወቂያ መላኪያ ትዕዛዝ (/announce) --
@dp.message(Command("announce"))
async def admin_announce(message: types.Message):
    if str(message.from_user.id) == str(ADMIN_CHAT_ID):
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            await message.answer("⚠️ እባክዎ ሊልኩት የሚፈልጉትን ማስታወቂያ አብረው ይጻፉ።\nምሳሌ: `/announce ሰላም ተጠቃሚዎች...`", parse_mode="HTML")
            return
        
        announcement_text = f"📢 <b>ማስታወቂያ ከዕዝ ክፍል</b>\n\n{args[1]}"
        success_count = 0
        
        for user_id in registered_users:
            try:
                await bot.send_message(chat_id=user_id, text=announcement_text, parse_mode="HTML")
                success_count += 1
            except:
                pass
                
        await message.answer(f"✅ ማስታወቂያው ለ <b>{success_count}</b> ተጠቃሚዎች ተልኳል!", parse_mode="HTML")
    else:
        await message.answer("ይህንን ትዕዛዝ ለመጠቀም ፈቃድ የለዎትም።")

# ከቴሌግራም ዌብ አፕ የሚመጣ መረጃ መቀበያ
@dp.message(F.web_app_data)
async def handle_web_app_data(message: types.Message):
    data_json = message.web_app_data.data
    user_id = message.from_user.id
    
    await message.answer("መረጃዎ እና የኬዋይሲ ሰነድዎ ለአድሚን ተልኳል! እባክዎ ሲረጋገጥ ይጠብቁ።")
    
    if ADMIN_CHAT_ID:
        try:
            parsed = json.loads(data_json)
            info_text = f"ስም: {parsed.get('firstName')} {parsed.get('fatherName')}\nስልክ: {parsed.get('phoneNumber')}"
        except:
            info_text = data_json

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ አጽድቅ (Approve Wallet)", callback_data=f"approve_{user_id}")]
        ])
        
        admin_text = f"🔔 <b>አዲስ የኬዋይሲ/ምዝገባ ጥያቄ መጥቷል!</b>\n\nተጠቃሚ ID: {user_id}\n{info_text}"
        await bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_text, reply_markup=keyboard, parse_mode="HTML")

# አድሚኑ አጽድቅ ሲል
@dp.callback_query(F.data.startswith("approve_"))
async def approve_user(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    if len(parts) > 1 and parts[1] != "web":
        target_user_id = parts[1]
        try:
            await bot.send_message(
                chat_id=target_user_id, 
                text="🎉 <b>እንኳን ደስ አለዎት!</b>\n\nየእርስዎ ኬዋይሲ (KYC) በአድሚን ጸድቋል። አሁን ዋሌትዎ ክፍት ነው!", 
                parse_mode="HTML"
            )
            await callback.message.edit_text(callback.message.text + "\n\n<b>[✅ ጸድቋል]</b>", parse_mode="HTML")
            await callback.answer("ተጠቃሚው በተሳካ ሁኔታ ጸድቋል!")
        except Exception as e:
            await callback.answer(f"ስህተት ተፈጥሯል: {e}", show_alert=True)
    else:
        await callback.message.edit_text(callback.message.text + "\n\n<b>[✅ የዌብ ተጠቃሚ ጸድቋል]</b>", parse_mode="HTML")
        await callback.answer("ተጠቃሚው ጸድቋል!")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
