import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import httpx

# የሰጧቸው ቶከኖች እና መረጃዎች
TOKEN = "8543715567:AAFPG7v8h-YJchs6aCYZ_Tad_35-iELISLw"
ADMIN_CHAT_ID = 5351353727
CHASECK_SECRET_KEY = "CHASECK-SncZN81Mx80yQcPiXJwRXDF6MdgchtNV"

# የባንክ መረጃዎች
BANK_INFO = {
    "bank_name": "Commercial Bank of Ethiopia (CBE) / ብሔራዊ ባንክ",
    "account_number": "100070780201",
    "account_name": "ጋሻዬ በጅጉ ሄሪጎ (Gashaye Bejigu Herigo)",
    "phone": "0916039015"
}

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
    # ሰርቨሩን የሚከፍትበት ሊንክ (Railway ላይ ዲፕሎይ ሲደረግ ራሱ ዩአርኤሉን ይይዛል)
    web_app_url = "https://mala-bot-production.up.railway.app/index.html"
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📒 ጋሻዬ ሀዋሳ - የእቁብ መመዝገቢያ ደብተር", web_app=WebAppInfo(url=web_app_url))]
        ]
    )
    
    welcome_text = (
        "💡 **እንኳን ወደ ጋሻዬ ሀዋሳ ሚስጥራዊ የእቁብ መመዝገቢያ ደብተር በሰላም መጡ!**\n\n"
        "🏦 **የባንክ መረጃዎቻችን:**\n"
        f"• ባንክ: {BANK_INFO['bank_name']}\n"
        f"• ሂሳብ ቁጥር: `{BANK_INFO['account_number']}`\n"
        f"• ስም: {BANK_INFO['account_name']}\n\n"
        "🚀 **እቁብ ለመመዝገብ እና ደብተሩን ለመክፈት ከታች ያለውን ቁልፍ ይጫኑ!**"
    )
    
    await message.answer(welcome_text, reply_markup=keyboard, parse_mode="Markdown")

@app.get("/index.html", response_class=HTMLResponse)
async def get_index():
    # ፋይሉን በቀጥታ አንብቦ ለቴሌግራም ሚኒ አፕ እንዲሰጥ ማድረግ ይቻላል
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        return html_content
    except Exception as e:
        return f"<h3>የአይቲ ስህተት ተፈጥሯል: {str(e)}</h3>"

@app.post("/api/save-booking")
async def save_booking(request: Request):
    try:
        data = await request.json()
        ticket_number = data.get("ticket_number")
        name = data.get("name")
        phone = data.get("phone")
        pay_status = data.get("pay_status")

        # ለአድሚን ማሳወቂያ መላክ ከፈለጉ እዚህ ጋር ማካተት ይቻላል
        await bot.send_message(
            ADMIN_CHAT_ID,
            f"🔔 **አዲስ የእቁብ ምዝገባ ተካሂዷል!**\n\n"
            f"🎟️ ቁጥር: {ticket_number}\n"
            f"👤 ስም: {name}\n"
            f"📞 ስልክ: {phone}\n"
            f"💳 ክፍያ: {pay_status}"
        )

        return {"status": "success", "message": "Booking saved successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

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
    main_loop = asyncio.get_event_loop()
    main_loop.run_until_complete(main())
