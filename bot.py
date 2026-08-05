import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import httpx

# የእርስዎ ትክክለኛ ቶክኖች እና መረጃዎች
TOKEN = "8543715567:AAFPG7v8h-YJchs6aCYZ_Tad_35-iELISLw"
ADMIN_CHAT_ID = 5351353727
CHASECK_SECRET_KEY = "CHASECK-SncZN81Mx80yQcPiXJwRXDF6MdgchtNV"
WEB_APP_URL = "https://gashayeb-spec.github.io/mala-bot/index.html"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🚀 መላ አፕ ክፈት", web_app=WebAppInfo(url=WEB_APP_URL))]
        ]
    )
    
    welcome_text = (
        "💡 **ብልህ ሰዎች ቀለል ያለውን መንገድ ይመርጣሉ**\n\n"
        "ብልህ ምርጫ የሚያደርግ ሰው ይሁኑ።\n\n"
        "🚀 **Telegram Premium ያግኙና ይደስቱ:-**\n"
        "✅ ፈጣን ዳውንሎድ\n"
        "✅ ትልቅ ፋይሎችን መላክ\n"
        "✅ የPremium ልዩ ባህሪያት\n\n"
        "📥 **Telegram Premiumን ዛሬውኑ ከ መላ ያግኙ!**"
    )
    
    await message.answer(welcome_text, reply_markup=keyboard, parse_mode="Markdown")

@app.post("/api/pay")
async def create_chapa_payment(request: Request):
    data = await request.json()
    amount = data.get("amount", 1399)
    first_name = data.get("first_name", "Gashaye")
    last_name = data.get("last_name", "Bejigu")
    recipient = data.get("recipient", "Koket_X")
    
    tx_ref = f"mala-tx-{int(asyncio.get_event_loop().time())}"

    payload = {
        "amount": str(amount),
        "currency": "ETB",
        "email": f"user_{tx_ref}@mala.et",
        "first_name": first_name,
        "last_name": last_name,
        "phone_number": "0916039015",
        "tx_ref": tx_ref,
        "callback_url": WEB_APP_URL,
        "return_url": WEB_APP_URL,
        "customization": {
            "title": "መላ ፕሪሚየም አገልግሎት",
            "description": f"Recipient: {recipient}"
        }
    }

    headers = {
        "Authorization": f"Bearer {CHASECK_SECRET_KEY}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post("https://api.chapa.co/v1/transaction/initialize", json=payload, headers=headers)
        result = response.json()
        
        try:
            await bot.send_message(
                ADMIN_CHAT_ID, 
                f"🔔 አዲስ የክፍያ ሙከራ!\n\n💰 ዋጋ: {amount} ETB\n👤 ተጠቃሚ: {first_name}\n🎯 ሪሲፒንት: {recipient}\nref: {tx_ref}"
            )
        except Exception as e:
            logging.error(f"Admin notification error: {e}")
            
        return result

async def main():
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    config = uvicorn.Config(app, host="0.0.0.0", port=port, log_level="info")
    server = uvicorn.Server(config)
    
    await asyncio.gather(
        dp.start_polling(bot),
        server.serve()
    )

if __name__ == "__main__":
    asyncio.run(main())
