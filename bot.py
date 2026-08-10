import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
# Render ላይ የሰጡትን የሰርቨር ሊንክ እዚህ ያስገቡ (ለምሳሌ፡ https://mela-bot.onrender.com)
WEB_APP_URL = "https://mela-bot.onrender.com" 

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
struct async def start_cmd(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 መተግበሪያውን ክፈት (Open Mela)", web_app=WebAppInfo(url=WEB_APP_URL))]
    ])
    await message.answer("ሰላም! ማላን ለመጠቀም ከታች ያለውን ቁልፍ ይጫኑ፦", reply_markup=kb)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
