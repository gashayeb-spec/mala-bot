import requests
from fastapi import FastAPI, Form, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse

app = FastAPI()

# የቴሌግራም ቦት መረጃዎ (እዚህጋ የባለቤቱን ቶክን እና የአድሚን ቻት 🆔 ያስገቡ)
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN"
ADMIN_CHAT_ID = "YOUR_ADMIN_USER_ID"

@app.post("/api/register-equb")
async def register_equb(
    full_name: str = Form(...),
    address: str = Form(...),
    phone: str = Form(...),
    cheque_no: str = Form(None),
    cycle_amount: float = Form(...),
    paid_amount: float = Form(...),
    remaining_due: float = Form(...),
    current_week: int = Form(...),
    guarantor_name: str = Form(None),
    guarantor_cheque: str = Form(None),
    collateral: str = Form(None),
    screenshot: UploadFile = File(...)
):
    try:
        # 1. የተጠቃሚውን መረጃ ለቴሌግራም አድሚን በጽሁፍ ማዘጋጀት
        caption = (
            f"🔔 **አዲስ የዕቁብ ምዝገባ እና ክፍያ!**\n\n"
            f"👤 **ስም:** {full_name}\n"
            f"📍 **አድራሻ:** {address}\n"
            f"📞 **ስልክ:** {phone}\n"
            f"🎫 **የቼክ ቁጥር:** {cheque_no or 'የለውም'}\n"
            f"💰 **የዙር መጠን:** {cycle_amount} ብር\n"
            f"💵 **የከፈለው:** {paid_amount} ብር\n"
            f"📉 **ቀሪ እዳ:** {remaining_due} ብር\n"
            f"📅 **ሳምንት:** {current_week} (ከ 5000)\n"
            f"🤝 **የዋስ ስም:** {guarantor_name or 'የለውም'}\n"
            f"📋 **የዋስ ቼክ:** {guarantor_cheque or 'የለውም'}\n"
            f"🚗 **ንብረት ዋስትና:** {collateral or 'የለውም'}"
        )

        # 2. ስክሪንሾቱን እና መረጃውን በቀጥታ ወደ ቴሌግራም ቦት መላክ
        file_bytes = await screenshot.read()
        telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
        
        files = {'photo': (screenshot.filename, file_bytes, screenshot.content_type)}
        data = {'chat_id': ADMIN_CHAT_ID, 'caption': caption, 'parse_mode': 'Markdown'}

        response = requests.post(telegram_url, data=data, files=files)
        
        if response.status_code == 200:
            return {"status": "success", "message": "Successfully sent to Telegram"}
        else:
            raise HTTPException(status_code=400, detail="Telegram API error")

    except Exception as e:
        return {"status": "error", "message": str(e)}
