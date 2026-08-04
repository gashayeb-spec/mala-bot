import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton

# የቦትዎ ቶከን
TOKEN = "8543715567:AAFPG7v8h-YJchs6aCYZ_Tad_35-iELISLw"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    # ትክክለኛው የ GitHub Pages የዌብሳይት ሊንክ (index.html ተካትቷል)
    web_app_url = "https://gashayeb-spec.github.io/mala-bot/index.html" 
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🚀 Mala አፕ ክፈት", web_app=WebAppInfo(url=web_app_url))]
        ]
    )
    
    welcome_text = (
        "💡 **ብዙ ሰዎች ቀለል ያለን መንገድ ይመርጣሉ**\n\n"
        "ለስንት ጊዜም በTelegram ገጾች እየተፈተኑ ቆዩአችሁ? "
        "ብዙ ምርጫ የሚሰርቅ ሰው ይሁኑ።\n\n"
        "🚀 **Telegram Premium ያገኙና ይደስቱ:-**\n"
        "✅ ፈጣን ዳውንሎድ\n"
        "✅ ትልቅ ፋይሎችን መላክ\n"
        "✅ የPremium ልዩ ባህሪያት\n"
        "✅ የተሻለ እና ምቹ የTelegram ልምድ\n\n"
        "📥 **Telegram Premiumን ዛሬውኑ ከ Mala ያገኙ!**"
    )
    
    await message.answer(welcome_text, reply_markup=keyboard, parse_mode="Markdown")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
