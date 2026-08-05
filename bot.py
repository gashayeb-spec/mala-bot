import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import httpx

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
            [InlineKeyboardButton(text="🚀 Mala አፕ ክፈት", web_app=WebAppInfo(url=WEB_APP_URL))]
        ]
    )
    
    if message.text and len(message.text) > 7:
        reg_data = message.text[7:]
        try:
            admin_kb = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(text="✅ አረጋግጥ (Approve)", callback_data=f"app_yes_{message.from_user.id}"),
                        InlineKeyboardButton(text="❌ ውድቅ (Reject)", callback_data=f"app_no_{message.from_user.id}")
                    ],
                    [
                        InlineKeyboardButton(text="🚫 አግድ (Block)", callback_data=f"app_block_{message.from_user.id}")
                    ]
                ]
            )
            
            notification_text = (
                f"🚨 **አዲስ የተጠቃሚ ምዝገባ ጥያቄ!**\n\n"
                f"👤 ተጠቃሚ ID: {message.from_user.id}\n"
                f"🔗 ዩዘርናም: @{message.from_user.username}\n"
                f"📝 ዝርዝር መረጃ:\n{reg_data}\n\n"
                f"እባክዎ ከታች ያሉትን ቁልፎች በመጫን ይወስኑ:"
            )
            
            await bot.send_message(chat_id=ADMIN_CHAT_ID, text=notification_text, reply_markup=admin_kb, parse_mode="Markdown")
            await message.answer("✅ መረጃዎ ለአድሚን ተልኳል። እባክዎ ማረጋገጫ ይጠብቁ...")
            return
        except Exception as e:
            logging.error(f"Error sending to admin: {e}")

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

@dp.callback_query(F.data.startswith("app_"))
async def process_admin_action(callback: types.CallbackQuery):
    data_parts = callback.data.split("_")
    action_type = data_parts[1]
    target_user_id = data_parts[2]
    
    if action_type == "yes":
        await callback.message.edit_text(callback.message.text + "\n\n✅ **ይህ አካውንት በአድሚን ጸድቋል (Approved)!**", parse_mode="Markdown")
        try:
            user_kb = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="🚀 አሁን አፑን ክፈት", web_app=WebAppInfo(url=WEB_APP_URL))]
                ]
            )
            await bot.send_message(
                chat_id=target_user_id, 
                text="🎉 **እንኳን ደስ አለዎት!** አካውንትዎ በአድሚን ጸድቋል። አሁን አፑን በመክፈት መጠቀም ይችላሉ።", 
                reply_markup=user_kb,
                parse_mode="Markdown"
            )
        except Exception as e:
            logging.error(f"Error notifying user: {e}")
            
        await callback.answer("አካውንቱ ጸድቋል!")
        
    elif action_type == "no":
        await callback.message.edit_text(callback.message.text + "\n\n❌ **ይህ ምዝገባ ውድቅ ተደርጓል (Rejected)!**", parse_mode="Markdown")
        try:
            await bot.send_message(
                chat_id=target_user_id, 
                text="❌ **የምዝገባ ጥያቄዎ ውድቅ ተደርጓል።** እባክዎ ትክክለኛ መረጃ በመሙላት እንደገና ይሞክሩ (Retry)."
            )
        except:
            pass
        await callback.answer("ምዝገባው ውድቅ ተደርጓል!")
        
    elif action_type == "block":
        await callback.message.edit_text(callback.message.text + "\n\n🚫 **ይህ ተጠቃሚ ታግዷል (Blocked)!**", parse_mode="Markdown")
        try:
            await bot.send_message(chat_id=target_user_id, text="🚫 አካውንትዎ በአድሚን ታግዷል።")
        except:
            pass
        await callback.answer("ተጠቃሚው ታግዷል!")

@app.post("/api/pay")
async def create_chapa_payment(request: Request):
    data = await request.json()
    amount = data.get("amount")
    email = data.get("email", "customer@mala.et")
    first_name = data.get("first_name", "Mala")
    last_name = data.get("last_name", "User")
    phone_number = data.get("phone_number", "0911000000")
    
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
    port = int(os.environ.get("PORT", 8080))
    config = uvicorn.Config(app, host="0.0.0.0", port=port, log_level="info")
    server = uvicorn.Server(config)
    
    await asyncio.gather(
        dp.start_polling(bot),
        server.serve()
    )

if __name__ == "__main__":
    asyncio.run(main())
