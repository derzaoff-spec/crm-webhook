from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# 👉 BU YERGA BITRIX WEBHOOK QO'Y
BITRIX_WEBHOOK = "https://derza.bitrix24.kz/rest/1/r1hgjqdeoyhdtx1n/"

def get_contact_phone(contact_id):
    try:
        url = BITRIX_WEBHOOK + "crm.contact.get.json"
        response = requests.get(url, params={"id": contact_id})
        data = response.json()

        phones = data.get("result", {}).get("PHONE", [])

        if phones:
            return phones[0]["VALUE"]

        return None

    except Exception as e:
        print("ERROR:", e)
        return None


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    print("RAW DATA:", data)

    contact_id = data.get("contact_id")
    deal_id = data.get("deal_id")

    phone = None

    if contact_id:
        phone = get_contact_phone(contact_id)

    print("CONTACT_ID:", contact_id)
    print("PHONE:", phone)

    return jsonify({
        "status": "ok",
        "phone": phone,
        "received": data
    })


@app.route("/", methods=["GET"])
def home():
    return "CRM Webhook ishlayapti 🚀"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)