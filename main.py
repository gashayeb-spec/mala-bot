import os
from flask import Flask, render_template, request, jsonify
import telebot
from dotenv import load_dotenv

# አካባቢያዊ ውቅሮችን ከ .env ፋይል ማንበብ
load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN", "YOUR_BOT_TOKEN")
CHAPA_SECRET = os.getenv("CHAPA_SECRET_KEY", "YOUR_CHAPA_SECRET_KEY")
WEBAPP_URL = os.getenv("WEBAPP_URL", "")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)


@app.route("/")
def index():
  """የድር ገጹን (Frontend) የሚያሳይ ዋናው ራውት"""
  return render_template("index.html")


@app.route("/api/pay", methods=["POST"])
def process_payment():
  """ከድረ-ገጹ የሚመጣውን የክፍያ መረጃ የሚቀበል ኤፒአይ"""
  data = request.json
  phone = data.get("phone")
  amount = data.get("amount")

  # እዚህጋ የክፍያ ማረጋገጫ ወይም የቻፓ (Chapa) ክፍያ ማቀናበሪያ ኮድ ይጻፋል
  print(f"ክፍያ ተቀብሏል - ስልክ: {phone}, መጠን: {amount}")

  return jsonify(
      {"status": "success", "message": "ክፍያዎ በተሳካ ሁኔታ ተጀምሯል!"}
  )


@bot.message_handler(commands=["start"])
def send_welcome(message):
  """ቦቱ ሲጀመር ሰላምታ እና የዌብ አፕ አገናኝ (Button) የሚልክ ትዕዛዝ"""
  markup = telebot.types.InlineKeyboardMarkup()
  # ዌብ አፕ ሊንኩን እዚህ ጋር ማስገባት ይቻላል
  web_app = telebot.types.WebAppInfo(url=WEBAPP_URL)
  markup.add(
      telebot.types.InlineKeyboardButton(
          text="🌐 መተግበሪያውን ክፈት", web_app=web_app
      )
  )

  bot.reply_to(
      message,
      "ሰላም! ከታች ያለውን ቁልፍ በመጫን መተግበሪያውን መክፈት ይችላሉ።",
      reply_markup=markup,
  )


if __name__ == "__main__":
  # ዌብ አፕሊኬሽኑን ማስጀመር
  app.run(host="0.0.0.0", port=5000, debug=True)
