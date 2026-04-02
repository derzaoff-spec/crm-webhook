from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

BITRIX_WEBHOOK = "https://derza.bitrix24.kz/rest/1/bwmu5i9lq63ur1jc/"

def format_phone(phone):
    if phone and phone.startswith("998"):
        return phone[3:]
    return phone

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    
    print("Keldi:", data)

    phone = data.get("phone") or data.get("caller") or data.get("from")
    formatted = format_phone(phone)

    print("Asl:", phone)
    print("Kesilgan:", formatted)

    response = requests.post(
        BITRIX_WEBHOOK + "crm.lead.add.json",
        json={
            "fields": {
                "TITLE": "Qo'ng'iroq",
                "PHONE": [{"VALUE": formatted, "VALUE_TYPE": "WORK"}]
            }
        }
    )

    print("Bitrix javobi:", response.text)

    return jsonify({"status": "ok"})

import os

app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))