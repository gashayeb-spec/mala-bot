import os
import json
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
import requests

app = FastAPI()

# ሚስጥራዊ ቁልፎች ከባካኤንድ Environment Variables ይነበባሉ
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN")
ADMIN_TELEGRAM_ID = os.getenv("ADMIN_TELEGRAM_ID", "YOUR_ADMIN_ID")
CHAPA_SECRET_KEY = os.getenv("CHAPA_SECRET_KEY", "YOUR_CHAPA_SECRET_KEY")
CHAPA_PUBLIC_KEY = os.getenv("CHAPA_PUBLIC_KEY", "YOUR_CHAPA_PUBLIC_KEY")

DATA_FILE = "koketi_equb_data.json"

def load_db():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"members": {}}

def save_db(db):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=4)

class EqubRegistration(BaseModel):
    full_name: str
    phone: str
    cheque_no: str
    cycle_amount: float
    paid_amount: float
    remaining_due: float
    guarantor_name: str
    guarantor_cheque: str
    collateral: str
    current_week: int

@app.post("/api/register-equb")
def register_equb(data: EqubRegistration):
    db = load_db()
    member_id = data.phone
    
    db["members"][member_id] = {
        "full_name": data.full_name,
        "phone": data.phone,
        "cheque_no": data.cheque_no,
        "cycle_amount": data.cycle_amount,
        "paid_amount": data.paid_amount,
        "remaining_due": data.remaining_due,
        "guarantor_name": data.guarantor_name,
        "guarantor_cheque": data.guarantor_cheque,
        "collateral": data.collateral,
        "current_week": data.current_week,
        "status": "Pending Approval"
    }
    save_db(db)
    
    # ለአድሚን በቴሌግራም ማሳወቂያ መላክ
    msg = (
        f"🚨 **አዲስ የዕቁብ ምዝገባ እና ክፍያ!**\n\n"
        f"👤 ስም: {data.full_name}\n"
        f"📞 ስልክ: {data.phone}\n"
        f"💰 የዕቁብ መጠን: {data.cycle_amount} ብር\n"
        f"💵 የከፈለው: {data.paid_amount} ብር\n"
        f"📅 ሳምንት: {data.current_week}\n"
        f"🤝 ዋስ: {data.guarantor_name} ({data.collateral})"
    )
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": ADMIN_TELEGRAM_ID, "text": msg, "parse_mode": "Markdown"})
    
    return {"status": "success", "message": "ምዝገባው በተሳካ ሁኔታ ተልኳል!"}

@app.get("/api/get-member/{phone}")
def get_member(phone: str):
    db = load_db()
    if phone in db["members"]:
        return {"status": "found", "data": db["members"][phone]}
    raise HTTPException(status_code=404, detail="አባል አልተገኘም")
