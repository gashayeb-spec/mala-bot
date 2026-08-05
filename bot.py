import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types, F
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
        "ለምን አሁንም በTelegram ገጾች እየተፈተኑ ቆዩአችሁ?\n"
        "ብልህ ምርጫ የሚያደርግ ሰው ይሁኑ።\n\n"
        "🚀 **Telegram Premium ያግኙና ይደስቱ:-**\n"
        "✅ ፈጣን ዳውንሎድ\n"
        "✅ ትልቅ ፋይሎችን መላክ\n"
        "✅ የPremium ልዩ ባህሪያት\n"
        "✅ የተሻለ እና ምቹ የTelegram ተሞክሮ\n\n"
        "📥 **Telegram Premiumን ዛሬውኑ ከ መላ ያግኙ!**"
    )
    
    await message.answer(welcome_text, reply_markup=keyboard, parse_mode="Markdown")

@app.post("/api/pay")
async def create_chapa_payment(request: Request):
    data = await request.json()
    amount = data.get("amount")
    email = data.get("email", "customer@mala.et")
    first_name = data.get("first_name", "Gashaye")
    last_name = data.get("last_name", "Bejigu")
    phone_number = data.get("phone_number", "0916039015")
    
    tx_ref = f"mala-tx-{int(asyncio.get_event_loop().time())}"

    payload = {
        "amount": str(amount),
        "currency": "ETB",
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "phone_number": phone_number,
        "tx_ref": tx_ref,
        "callback_url": WEB_APP_URL,
        "return_url": WEB_APP_URL
    }

    headers = {
        "Authorization": f"Bearer {CHASECK_SECRET_KEY}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post("https://api.chapa.co/v1/transaction/initialize", json=payload, headers=headers)
        result = response.json()
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
