import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton

# የቦትዎ ቶከን
TOKEN = "8543715567:AAFPG7v8h-YJchs6aCYZ_Tad_35-iELISLw"

# 🔑 የአድሚኑ (የእርስዎ) ትክክለኛ የቴሌግራም ቻት አይዲ
ADMIN_CHAT_ID = 5351353727

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    # ተጠቃሚው ወደ ቦቱ ሲመጣ የሚከፈተው ሊንክ
    web_app_url = "https://gashayeb-spec.github.io/mala-bot/index.html" 
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🚀 Mala አፕ ክፈት", web_app=WebAppInfo(url=web_app_url))]
        ]
    )
    
    # ተጠቃሚው ከሚኒ አፑ መረጃውን ልኮ ወደ ቦቱ ሲመጣ (በ Start link በኩል ሲገባ) የሚቀበለው ሎጂክ
    if message.text and len(message.text) > 7:
        reg_data = message.text[7:] # reg_ ብሎ የሚጀምረውን ዳታ መቀበል
        try:
            # መረጃውን ለአድሚን (ለእርስዎ) መላክ
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

# አድሚኑ የሚጫናቸውን አዝራሮች (Approve, Reject, Block) ማስተናገጃ
@dp.callback_query(F.data.startswith("app_"))
async def process_admin_action(callback: types.CallbackQuery):
    data_parts = callback.data.split("_")
    action_type = data_parts[1] # yes, no, block
    target_user_id = data_parts[2]
    
    if action_type == "yes":
        await callback.message.edit_text(callback.message.text + "\n\n✅ **ይህ አካውንት በአድሚን ጸድቋል (Approved)!**", parse_mode="Markdown")
        try:
            await bot.send_message(chat_id=target_user_id, text="🎉 አካውንትዎ በአድሚን ጸድቋል! አሁን ሚኒ አፑን በመክፈት መጠቀም ይችላሉ።")
        except:
            pass
        await callback.answer("አካውንቱ ጸድቋል!")
        
    elif action_type == "no":
        await callback.message.edit_text(callback.message.text + "\n\n❌ **ይህ ምዝገባ ውድቅ ተደርጓል (Rejected)!**", parse_mode="Markdown")
        try:
            await bot.send_message(chat_id=target_user_id, text="❌ የምዝገባ ጥያቄዎ ውድቅ ተደርጓል። እባክዎ ትክክለኛ መረጃ እንደገና ይሞክሩ።")
        except:
            pass
        await callback.answer("ምዝገባው ውድቅ ተደርጓል!")
        
    elif action_type == "block":
        await callback.message.edit_text(callback.message.text + "\n\n🚫 **ይህ ተጠቃሚ ታግዷል (Blocked)!**", parse_mode="Markdown")
        try:
            await bot.send_message(chat_id=target_user_id, text="🚫 አካውንትዎ ታግዷል።")
        except:
            pass
        await callback.answer("ተጠቃሚው ታግዷል!")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
