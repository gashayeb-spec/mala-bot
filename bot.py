import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from dotenv import load_dotenv

# .env ፋይል ውስጥ ያሉትን መረጃዎች እንጭናለን
load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

# ቦቱን እና ዲሲፓቸርን እናስጀምራለን
bot = Bot(token=TOKEN)
dp = Dispatcher()

# /start ሲባል የሚሰጠው ምላሽ
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    # ሚኒ አፕ የሚከፈትበት የዌብሳይት ሊንክ (በኋላ ወደ ሬንደር ስትጭን ትቀይረዋለህ)
    # ለምሳሌ: "https://mela-bot.onrender.com"
    web_app_url = "https://your-webapp-link.com" 

    # የመቀበያ መልእክት
    text = (
        f"ሰላም {message.from_user.full_name}! 👋\n\n"
        "እንኳን ወደ <b>Mela-bot</b> በደህና መጡ! 🚀\n\n"
        "እዚህ የሶሻል ሚዲያ አገልግሎቶችን (Telegram Premium, TikTok Coins, Stars) "
        "በቀላሉ ማዘዝ ይችላሉ። ከታች ያለውን በተን በመጫን ወደ አፕሊኬሽኑ ይግቡ።"
    )

    # አፕሊኬሽኑን የሚከፍት በተን
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🚀 Mela-bot ን ይክፈቱ", 
            web_app=WebAppInfo(url=web_app_url)
        )]
    ])

    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")

# ቦቱን ማስጀመሪያ
async def main():
    print("Mela-bot እየሰራ ነው...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
