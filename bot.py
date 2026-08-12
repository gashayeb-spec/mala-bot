import os
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

BOT_TOKEN = "8543715567:AAEeL0HgHcw62LhGaj3tNn9yJp2bh5XdmfM"
ADMIN_CHAT_ID = "5351353727" 
CHAPA_PUBLIC_KEY = "CHAPUBK-hLBEJPiKDlRpfBCqTczyE1OsnrrK3Zhj"
CHASECK_SECRET_KEY = "CHASECK-SncZN81Mx80yQcPiXJwRXDF6MdgchtNV"

WEB_APP_URL = "https://mela-bot.onrender.com"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

registered_users = set()
user_status = {}  # የተጠቃሚዎችን ስቴተስ ለመያዝ (pending, approved, cancelled, blocked)
bot_loop = None

app = Flask(__name__, template_folder='.')

@app.route('/')
def home():
    return render_template('index.html')

# -- CORS ማስተካከያ (Headers) --
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS'
    return response

# -- ተጠቃሚው የጸደቀ መሆኑን በዌብሳይቱ በኩል ለማረጋገጥ የሚረዳ ኤፒአይ --
@app.route('/check-status', methods=['GET'])
def check_status():
    user_id = request.args.get('user_id')
    status = user_status.get(str(user_id), 'pending')
    return jsonify({"status": status})

@app.route('/submit-registration', methods=['POST'])
def submit_registration():
    try:
        data = request.json
        user_id = str(data.get('telegramId', ''))
        first_name = data.get('firstName', '')
        father_name = data.get('fatherName', '')
        grand_father_name = data.get('grandFatherName', '')
        mother_name = data.get('motherName', '')
        phone = data.get('phoneNumber', '')
        nid = data.get('nationalIdNumber', '')
        
        user_status[user_id] = 'pending'
        
        info_text = (
            f"👤 <b>አዲስ የዌብ ምዝገባ/ኬዋይሲ ጥያቄ!</b>\n\n"
            f"• መለያ (ID): <code>{user_id}</code>\n"
            f"• ስም: <b>{first_name} {father_name} {grand_father_name}</b>\n"
            f"• የእናት ስም: {mother_name}\n"
            f"• ስልክ ቁጥር: {phone}\n"
            f"• ብሔራዊ መታወቂያ No: <code>{nid}</code>"
        )
        
        # አድሚኑ የሚጠቀምባቸው አማራጮች (አጽድቅ፣ ሰርዝ፣ አግድ)
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ አጽድቅ", callback_data=f"approve_{user_id}"),
                InlineKeyboardButton(text="❌ ሰርዝ", callback_data=f"cancel_{user_id}")
            ],
            [
                InlineKeyboardButton(text="🚫 አግድ (Block)", callback_data=f"block_{user_id}")
            ]
        ])
        
        if bot_loop and bot_loop.is_running():
            asyncio.run_coroutine_threadsafe(
                bot.send_message(chat_id=ADMIN_CHAT_ID, text=info_text, reply_markup=keyboard, parse_mode="HTML"),
                bot_loop
            )
        
        return jsonify({"status": "success", "message": "መረጃው ለአድሚን በተሳካ ሁኔታ ተልኳል"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# -- አጠቃላይ የኖቲፊኬሽን እና ግብይት መቀበያ API (CORS የሚፈታ) --
@app.route('/api/notify-admin', methods=['POST'])
def notify_admin():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400

        message_type = data.get('type', 'general')
        user_name = data.get('userName', 'ተጠቃሚ')
        telegram_id = data.get('telegramId', 'N/A')
        details = data.get('details', '')

        formatted_msg = (
            f"⚡ *[Mela-Bot አውቶማቲክ ሲስተም ሪፖርት]*\n"
            f"📌 ዓይነት: `{message_type}`\n"
            f"👤 ተጠቃሚ: {user_name} (ID: `{telegram_id}`)\n\n"
            f"📝 ዝርዝር መረጃ:\n{details}"
        )

        if bot_loop and bot_loop.is_running():
            asyncio.run_coroutine_threadsafe(
                bot.send_message(chat_id=ADMIN_CHAT_ID, text=formatted_msg, parse_mode="Markdown"),
                bot_loop
            )

        return jsonify({"success": True, "message": "Notification sent successfully!"}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/initiate-chapa', methods=['POST'])
def initiate_chapa():
    req_data = request.json
    amount = req_data.get('amount')
    email = req_data.get('email', 'user@mela.com')
    first_name = req_data.get('first_name', 'Mela')
    last_name = req_data.get('last_name', 'User')
    phone = req_data.get('phone', '0911000000')
    
    tx_ref = f"mela-tx-{int(asyncio.get_event_loop().time())}"
    headers = {
        "Authorization": f"Bearer {CHASECK_SECRET_KEY}",
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
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    user_id = str(message.from_user.id)
    registered_users.add(user_id)
    
    if user_status.get(user_id) == 'blocked':
        await message.answer("🚫 አካውንትዎ ታግዷል። እባክዎ አድሚኑን ያግኙ።")
        return
        
    welcome_text = (
        "🌟 <b>እንኳን ወደ መላ.ቦት (Mela-bot) በደህና መጡ!</b> 🌟\n\n"
        "💰 <b>ደህንነቱ የተጠበቀ የዲጂታል ዋሌት እና የገንዘብ ዝውውር መድረክ።</b>\n\n"
        "📌 <i>ምን ማድረግ ይችላሉ?</i>\n"
        "• ዋሌት መክፈት እና ኬዋይሲ ማረጋገጥ።\n"
        "• በቻፓ (Chapa) ብር ማስገባት እና ማውጣት።\n"
        "• ሎተሪ መቁረጥ፣ P2P ሼር ማድረግ እና ኮይን መቀየር!\n\n"
        "👇 ለመጀመር ከታች ያለውን ቁልፍ ይጫኑ።"
    )
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🚀 ስታርት - ዋሌት ክፈት & ኬዋይሲ አድርግ", web_app=WebAppInfo(url=WEB_APP_URL))]
        ]
    )
    await message.answer(welcome_text, reply_markup=keyboard, parse_mode="HTML")

@dp.callback_query(F.data.startswith("approve_"))
async def approve_user_cb(callback: types.CallbackQuery):
    target_user_id = callback.data.split("_")[1]
    user_status[target_user_id] = 'approved'
    
    try:
        await bot.send_message(
            chat_id=target_user_id, 
            text="🎉 <b>እንኳን ደስ አለዎት!</b>\n\nየእርስዎ ኬዋይሲ (KYC) በአድሚን ጸድቋል። አሁን ወደ ዋሌትዎ ገብተው መጠቀም ይችላሉ!", 
            parse_mode="HTML"
        )
    except:
        pass
        
    await callback.message.edit_text(callback.message.text + "\n\n<b>[✅ ጸድቋል (Approved)]</b>", parse_mode="HTML")
    await callback.answer("ተጠቃሚው ተጸድቋል!")

@dp.callback_query(F.data.startswith("cancel_"))
async def cancel_user_cb(callback: types.CallbackQuery):
    target_user_id = callback.data.split("_")[1]
    user_status[target_user_id] = 'cancelled'
    
    try:
        await bot.send_message(
            chat_id=target_user_id, 
            text="❌ <b>የኬዋይሲ ጥያቄዎ ውድቅ ተደርጓል!</b>\n\nእባክዎ ትክክለኛ መረጃ እና መታወቂያ በመላክ እንደገና ይሞክሩ።", 
            parse_mode="HTML"
        )
    except:
        pass
        
    await callback.message.edit_text(callback.message.text + "\n\n<b>[❌ ውድቅ ተደርጓል (Cancelled)]</b>", parse_mode="HTML")
    await callback.answer("ጥያቄው ተሰርዟል!")

@dp.callback_query(F.data.startswith("block_"))
async def block_user_cb(callback: types.CallbackQuery):
    target_user_id = callback.data.split("_")[1]
    user_status[target_user_id] = 'blocked'
    
    try:
        await bot.send_message(
            chat_id=target_user_id, 
            text="🚫 <b>አካውንትዎ ታግዷል!</b>\n\nከአስተዳዳሪው ጋር ይነጋገሩ።", 
            parse_mode="HTML"
        )
    except:
        pass
        
    await callback.message.edit_text(callback.message.text + "\n\n<b>[🚫 ታግዷል (Blocked)]</b>", parse_mode="HTML")
    await callback.answer("ተጠቃሚው ታግዷል!")

async def main():
    global bot_loop
    bot_loop = asyncio.get_running_loop()
    threading.Thread(target=run_web, daemon=True).start()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
