from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

BITRIX_WEBHOOK = "https://derza.bitrix24.kz/rest/1/bwmu5i9lq63ur1jc/"

def format_phone(phone):
    if phone:
        phone = str(phone)
        if phone.startswith("998"):
            return phone[3:]
    return phone

@app.route('/')
def home():
    return "Server ishlayapti 🚀"

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    # 👉 Browser test uchun
    if request.method == 'GET':
        return "Webhook ishlayapti ✅"

    try:
        data = request.get_json(force=True)

        print("Keldi:", data)

        phone = data.get("phone") or data.get("caller") or data.get("from")

        if not phone:
            return jsonify({"error": "phone yo‘q"}), 400

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

    except Exception as e:
        print("Xatolik:", str(e))
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))