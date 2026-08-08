import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, html, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

# የቦት ቶኪን
TOKEN = "8543715567:AAG56vVGC2LDpIOED-euwwF72f-245TG27U"

# ትክክለኛው የእርስዎ የአድሚን ቴሌግራም አይዲ
ADMIN_ID = 5351353727

dp = Dispatcher()

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    web_app_url = "https://mela-bot-site.onrender.com"
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💳 ክፍያ ለመፈጸም (3 ወር - ETB 3599)", 
                    web_app=WebAppInfo(url=web_app_url)
                )
            ]
        ]
    )
    
    await message.answer(
        f"ሰላም {html.bold(message.from_user.full_name)}! ወደ መላ ቦት በደህና መጡ።\n\n"
        "📦 <b>ጥቅል:</b> 3 ወር (Telegram Premium)\n"
        "💰 <b>ጠቅላላ ዋጋ:</b> ETB 3599.00\n\n"
        "ክፍያ ለመፈጸም ከታች ያለውን ቁልፍ ይጫኑ:",
        reply_markup=keyboard
    )

# ከ Mini App የሚመጣውን መረጃ ወደ አድሚን (5351353727) የሚልክበት ክፍል
@dp.message(F.web_app_data)
async def handle_web_app_data(message: Message):
    user_data = message.web_app_data.data
    await message.bot.send_message(
        ADMIN_ID,
        f"📥 <b>አዲስ የክፍያ ጥያቄ ደርሷል!</b>\n\n"
        f"👤 <b>ዩዘር:</b> {message.from_user.full_name} (@{message.from_user.username})\n"
        f"🆔 <b>አይዲ:</b> {message.from_user.id}\n"
        f"📋 <b>ዝርዝር:</b> {user_data}"
    )
    await message.answer("✅ የክፍያ ጥያቄዎ በተሳካ ሁኔታ ተልኳል! እናመሰግናለን።")

async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
