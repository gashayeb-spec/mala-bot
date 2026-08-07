import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# የሎግ ማስተካከያ ስህተቶችን ለማየት
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TELEGRAM_TOKEN = "8543715567:AAFPG7v8h-YJchs6aCYZ_Tad_35-iELISLw"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("🌐 ዋሌት ለመክፈት (App ይክፈቱ)", web_app={"url": "https://yourdomain.com"})]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"ሰላም {user.first_name}! ወደ ዲጂታል ኪስ ቦርሳዎ በደህና መጡ።",
        reply_markup=reply_markup
    )

if __name__ == '__main__':
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    
    print("ቦቱ በመጀመር ላይ ነው...")
    application.run_polling(drop_pending_updates=True)
