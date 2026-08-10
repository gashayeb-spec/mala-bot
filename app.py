import os
from flask import Flask, render_template, request, jsonify
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, template_folder='.')

CHAPA_SECRET_KEY = os.getenv("CHAPA_SECRET_KEY")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/pay', methods=['POST'])
def pay():
    data = request.json
    amount = data.get('amount')
    email = data.get('email', 'user@mela.com')
    
    headers = {
        "Authorization": f"Bearer {CHAPA_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "amount": str(amount),
        "currency": "ETB",
        "email": email,
        "first_name": "Mela",
        "last_name": "User",
        "tx_ref": "mela-tx-" + os.urandom(4).hex(),
        "callback_url": "https://yourdomain.com/callback",
        "return_url": "https://t.me/your_bot_username"
    }
    
    response = requests.post("https://api.chapa.co/v1/transaction/initialize", json=payload, headers=headers)
    return jsonify(response.json())

if __name__ == '__main__':
    app.run(debug=True, port=5000)
