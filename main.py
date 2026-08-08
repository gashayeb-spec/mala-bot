import logging
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton

# የተሰጡዎት ቋሚ መረጃዎች
TOKEN = "8543715567:AAFPG7v8h-YJchs6aCYZ_Tad_35-iELISLw"
ADMIN_ID = 5351353727
CHAPA_SECRET_KEY = "CHASECK-SncZN81Mx80yQcPiXJwRXDF6MdgchtNV"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user = message.from_user
    full_name = user.full_name
    username = f"@{user.username}" if user.username else "No Username"
    
    logging.info(f"User started bot: {full_name} ({username}), ID: {user.id}")

    welcome_text = (
        f"👋 ሰላም {full_name} እንቋንቋ ደህና መጡ!\n\n"
        "📱 ፕሪሚየም አገልግሎቶችን ለማግኘት ከዚህ በታች ያለውን ቁልፍ ይጫኑ:\n"
        "• ቴሌግራም ፕሪሚየም\n"
        "• ማህበራዊ ሚዲያ አገልግሎቶች\n"
        "• ቲክቶክ ኮይንስ\n"
        "• እና ሌሎችም!"
    )
    
    # የሚኒ አፕ (Mini App) መክፈቻ ቁልፍ (የእርስዎን የሆስቲንግ ሊንክ እዚህ ያስገቡ)
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🚀 መላ ቦት ማኑዌል ክፈት", web_app=WebAppInfo(url="https://your-domain.com/index.html"))]
        ]
    )
    
    await message.answer(welcome_text, reply_markup=keyboard)

# የቻፓ ክፍያ ማቀናጃ ፌንክሽን
def initialize_chapa_payment(amount, email, first_name, last_name, phone, tx_ref):
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
        "tx_ref": tx_ref,
        "callback_url": "https://your-domain.com/api/chapa-webhook",
        "return_url": "https://t.me/your_bot_username"
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))
