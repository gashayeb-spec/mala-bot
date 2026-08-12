import logging
import requests
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio

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

# ከዌብ አፕ (HTML) የሚላኩ መረጃዎችን መቀበያ
@dp.message(F.web_app_data)
async def handle_web_app_data(message: types.Message):
    data = message.web_app_data.data
    await message.answer("መረጃዎ በተሳካ ሁኔታ ደርሷል! እናመሰግናለን።")
    
    if ADMIN_CHAT_ID:
        admin_text = f"🔔 <b>አዲስ የኬዋይሲ/ምዝገባ ጥያቄ መጥቷል!</b>\n\nተጠቃሚ: @{message.from_user.username}\nመረጃ: {data}"
        await bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_text, parse_mode="HTML")

# ቻፓ ክፍያ ማጀመሪያ ፉንክሽን (Chapa Initialization)
def initialize_chapa_payment(amount, email, first_name, last_name, phone):
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
        "last_name": last_name,
        "phone_number": phone,
        "tx_ref": f"mela-tx-{asyncio.get_event_loop().time()}",
        "callback_url": "https://webhook.site/callback",
        "return_url": "https://t.me/your_bot_username"
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
drop_pending_updates=True
