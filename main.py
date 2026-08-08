import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

# አዲሱ የቦት ቶኪን
TOKEN = "8543715567:AAG56vVGC2LDpIOED-euwwF72f-245TG27U"

dp = Dispatcher()

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    # ዌብ አድራሻውን (Render ላይ Static Site ከፈጠሩ በኋላ የሚሰጥዎትን ሊንክ ከታች ባለው ቦታ ያስገቡ)
    web_app_url = "https://mela-bot-site.onrender.com"
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💳 ክፍያ ለመፈጸም (Mini App)", 
                    web_app=WebAppInfo(url=web_app_url)
                )
            ]
        ]
    )
    
    await message.answer(
        f"ሰላም {html.bold(message.from_user.full_name)}! ወደ መላ ቦት በደህና መጡ።\nየቴሌግራም ፕሪሚየም ጥቅል ለመግዛት ከታች ያለውን ሊንክ ይጫኑ።",
        reply_markup=keyboard
    )

async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    # የድሮ Conflict ስህተት እንዳይፈጠር ከማስጀመርዎ በፊት ዌብሁክ ወይም አሮጌ ፖሊንግ ካለ ይጸዳል
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
