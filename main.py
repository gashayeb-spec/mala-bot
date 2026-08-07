import requests
from flask import Flask, request, jsonify, send_from_directory
import os

app = Flask(__name__)

# የቴሌግራም እና የቻፓ መረጃዎችዎ
TELEGRAM_BOT_TOKEN = "8543715567:AAFPG7v8h-YJchs6aCYZ_Tad_35-iELISLw"
ADMIN_CHAT_ID = "5351353727"
CHAPA_SECRET_KEY = "CHASECK-SncZN81Mx80yQcPiXJwRXDF6MdgchtNV"

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/api/register-equb', methods=['POST'])
def register_equb():
    try:
        data = request.form
        screenshot = request.files.get('screenshot')
        
        # ወደ ቴሌግራም የሚላከው መልእክት
        caption = (
            f"🔔 *አዲስ የዕቁብ ምዝገባ!*\n\n"
            f"👤 *ስም:* {data.get('full_name')}\n"
            f"📍 *አድራሻ:* {data.get('address')}\n"
            f"📞 *ስልክ:* {data.get('phone')}\n"
            f"🎫 *የቼክ ቁጥር:* {data.get('cheque_no') or 'የለም'}\n"
            f"💰 *የዙር መጠን:* {data.get('cycle_amount')} ብር\n"
            f"💵 *የከፈለው:* {data.get('paid_amount')} ብር\n"
            f"📉 *ቀሪ እዳ:* {data.get('remaining_due')} ብር\n"
            f"📅 *ሳምንት:* {data.get('current_week')} (ከ 5000)\n"
            f"🤝 *የዋስ ስም:* {data.get('guarantor_name') or 'የለም'}\n"
            f"📋 *የዋስ ቼክ:* {data.get('guarantor_cheque') or 'የለም'}\n"
            f"🚗 *ንብረት ዋስትና:* {data.get('collateral') or 'የለም'}"
        )
        
        telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
        
        files = {}
        if screenshot:
            files['photo'] = (screenshot.filename, screenshot.read(), screenshot.content_type)
            
        payload = {
            'chat_id': ADMIN_CHAT_ID, 
            'caption': caption, 
            'parse_mode': 'Markdown'
        }
        
        response = requests.post(telegram_url, data=payload, files=files)
        
        if response.status_code == 200:
            return jsonify({"status": "success"})
        else:
            return jsonify({"status": "error", "message": "Failed to send to Telegram"}), 500
            
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
