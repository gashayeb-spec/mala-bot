import os
import logging
import requests
from flask import Flask, request, jsonify, render_template_string

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Credentials & Config provided
BOT_TOKEN = "8543715567:AAFPG7v8h-YJchs6aCYZ_Tad_35-iELISLw"
ADMIN_CHAT_ID = "5351353727"
CHAPA_SECRET_KEY = "CHASECK-SncZN81Mx80yQcPiXJwRXDF6MdgehtNV"
SUPPORT_PHONE = "0916039015"
MPESA_NAME = "ጋሻዬ በጅጉ ሄሬጉ"

TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# In-memory mock database for users, wallet balances, pins, and orders
users_db = {
    5351353727: {
        "user_id": 5351353727,
        "username": "Koket_X",
        "full_name": "Gashaye Bejigu",
        "wallet_balance": 0.0,
        "wallet_pin": None,  # 4-digit PIN for wallet protection
        "orders": []
    }
}

# HTML Frontend Template for the Telegram Mini App
MINI_APP_HTML = """
<!DOCTYPE html>
<html lang="am">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ጠቃሚ Bot Mini App</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        body { background-color: #0f172a; color: #f8fafc; font-family: sans-serif; margin: 0; padding: 15px; padding-bottom: 70px; }
        .card { background: #1e293b; border-radius: 12px; padding: 15px; margin-bottom: 15px; border: 1px solid #334155; }
        h2, h3 { margin-top: 0; color: #38bdf8; }
        button { background: #2563eb; color: white; border: none; padding: 10px 15px; border-radius: 8px; width: 100%; font-size: 16px; cursor: pointer; margin-top: 10px; }
        button:active { background: #1d4ed8; }
        input, select { width: 100%; padding: 10px; margin-top: 5px; margin-bottom: 10px; background: #0f172a; border: 1px solid #475569; color: white; border-radius: 6px; box-sizing: border-box; }
        .nav-bar { position: fixed; bottom: 0; left: 0; width: 100%; background: #090d16; display: flex; justify-content: space-around; padding: 10px 0; border-top: 1px solid #1e293b; }
        .nav-item { color: #94a3b8; text-align: center; font-size: 12px; cursor: pointer; text-decoration: none; }
        .nav-item.active { color: #38bdf8; }
        .hidden { display: none; }
    </style>
</head>
<body>

    <div id="home-section" class="section">
        <h2>ጠቃሚ Bot - Services</h2>
        <div class="card">
            <h3>Telegram Premium</h3>
            <p>Upgrade to premium instantly</p>
            <button onclick="showTab('order-section')">Get Started</button>
        </div>
        <div class="card">
            <h3>TikTok Coins</h3>
            <p>Top up creator balances</p>
            <button onclick="alert('Coming soon!')">Get Started</button>
        </div>
    </div>

    <div id="order-section" class="section hidden">
        <h2>Telegram Premium</h2>
        <div class="card">
            <label>Duration Package:</label>
            <select id="duration" onchange="calculatePrice()">
                <option value="3600">3 Months - 3599 ETB</option>
                <option value="7000">6 Months - 6999 ETB</option>
                <option value="8900">1 Year - 8900 ETB</option>
            </select>
            
            <label>Price (ETB):</label>
            <input type="text" id="price-display" value="3599.00" readonly>
            
            <label>Telegram Username:</label>
            <input type="text" id="username" value="@Koket_X" readonly>

            <button onclick="payWithChapa()">Continue to Payment (Chapa)</button>
            <button onclick="payWithWallet()" style="background: #10b981;">Pay from Wallet</button>
        </div>
    </div>

    <div id="wallet-section" class="section hidden">
        <h2>My Wallet</h2>
        <div class="card" style="text-align: center;">
            <p>Balance</p>
            <h1 id="wallet-bal">0.00 ETB</h1>
            <button onclick="setupPin()">Set / Change Wallet PIN</button>
            <button onclick="depositMoney()" style="background: #059669;">Deposit Funds</button>
        </div>
    </div>

    <div class="nav-bar">
        <div class="nav-item active" onclick="showTab('home-section')">🏠 መነሻ</div>
        <div class="nav-item" onclick="showTab('order-section')">📦 ትዕዛዞች</div>
        <div class="nav-item" onclick="showTab('wallet-section')">💳 ዋሌት</div>
    </div>

    <script>
        const tg = window.Telegram.WebApp;
        tg.expand();

        function showTab(sectionId) {
            document.querySelectorAll('.section').forEach(s => s.classList.add('hidden'));
            document.getElementById(sectionId).classList.remove('hidden');
        }

        function calculatePrice() {
            const select = document.getElementById('duration');
            document.getElementById('price-display').value = select.value + ".00";
        }

        function payWithChapa() {
            alert("Connecting to Chapa Secure Payment Gateway... Support/Telebirr/CBE: {{ support_phone }} | M-Pesa Name: {{ mpesa_name }}");
        }

        function payWithWallet() {
            let pin = prompt("Enter your 4-digit Wallet PIN:");
            if(pin) {
                alert("Processing payment securely from your wallet...");
            }
        }

        function setupPin() {
            let pin = prompt("Create a new 4-digit PIN for your wallet security:");
            if(pin) {
                alert("Wallet PIN configured successfully!");
            }
        }

        function depositMoney() {
            alert("Deposit via Telebirr/CBE ({{ support_phone }}) or M-Pesa ({{ mpesa_name }})");
        }
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(MINI_APP_HTML, support_phone=SUPPORT_PHONE, mpesa_name=MPESA_NAME)

@app.route("/webhook", methods=["POST"])
def telegram_webhook():
    data = request.get_json()
    if not data:
        return jsonify({"status": "error"}), 400

    if "message" in data:
        message = data["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "")
        user_name = message["from"].get("first_name", "User")

        if text == "/start":
            reply_text = (
                f"ሰላም {user_name}! እንኳን ወደ ጠቃሚ Bot በደህና መጡ።\n\n"
                f"📞 የደንበኛ ድጋፍ / Telebirr / CBE Birr ቁጥር: {SUPPORT_PHONE}\n"
                f"👤 M-Pesa ስም: {MPESA_NAME}\n\n"
                "ከታች ያለውን ሊንክ በመጫን ሚኒ አፖን (Mini App) ተጠቅመው ትዕዛዞችን ማስተናገድ ይችላሉ።"
            )
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
                "chat_id": chat_id,
                "text": reply_text
            })

    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
