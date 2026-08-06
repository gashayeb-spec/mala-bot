from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
import os

app = FastAPI()

DATA_FILE = "gashaye_data.json"

# መረጃዎችን ከፋይል የመጫኛ እና የማስቀመጫ ሎጂክ
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"wallets": {}, "bookings": {}}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

class WalletCreate(BaseModel):
    user_id: str
    name: str
    phone: str

class BookingRequest(BaseModel):
    user_id: str
    ticket_number: int
    week: int
    pay_method: str
    amount: float

@app.post("/api/create-wallet")
def create_wallet(data: WalletCreate):
    db = load_data()
    if data.user_id in db["wallets"]:
        return {"status": "success", "message": "ዋሌት ቀደም ሲል አለ"}
    
    db["wallets"][data.user_id] = {
        "name": data.name,
        "phone": data.phone,
        "balance": 0.0,
        "transactions": []
    }
    save_data(db)
    return {"status": "success", "message": "ዋሌት በተሳካ ሁኔታ ተከፍቷል"}

@app.post("/api/fund-wallet")
def fund_wallet(user_id: str, amount: float):
    db = load_data()
    if user_id not in db["wallets"]:
        raise HTTPException(status_code=404,_detail="ዋሌት አልተገኘም")
    
    db["wallets"][user_id]["balance"] += amount
    db["wallets"][user_id]["transactions"].append(f"ገንዘብ ገብቷል: +{amount} ብር")
    save_data(db)
    return {"status": "success", "new_balance": db["wallets"][user_id]["balance"]}

@app.get("/api/get-bookings")
def get_bookings():
    db = load_data()
    return {"bookings": db["bookings"], "wallets": db["wallets"]}

@app.post("/api/save-booking")
def save_booking(req: BookingRequest):
    db = load_data()
    user_id = req.user_id
    
    if user_id not in db["wallets"]:
        raise HTTPException(status_code=400, detail="እባክዎ መጀመሪያ ዋሌት ይክፈቱ")
    
    # ከዋሌት ሂሳብ የመቀነስ ወይም ቀጥታ የማረጋገጥ ሎጂክ
    wallet = db["wallets"][user_id]
    if req.pay_method == "wallet":
        if wallet["balance"] < req.amount:
            return {"status": "error", "message": "በዋሌትዎ ውስጥ በቂ ገንዘብ የለም!"}
        wallet["balance"] -= req.amount
        wallet["transactions"].append(f"ለእቁብ ድርሻ {req.ticket_number} (ሳምንት {req.week}) ክፍያ ተፈጽሟል: -{req.amount} ብር")
    
    db["bookings"][str(req.ticket_number)] = {
        "user_id": user_id,
        "name": wallet["name"],
        "phone": wallet["phone"],
        "week": req.week,
        "pay": req.pay_method,
        "status": "approved" if req.pay_method == "wallet" else "pending"
    }
    save_data(db)
    return {"status": "success", "message": "ምዝገባው ተሳክቷል"}
