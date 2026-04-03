from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

BITRIX_WEBHOOK = "https://derza.bitrix24.kz/rest/1/r1hgjqdeoyhdtx1n/"

# 👉 Dealdan contact_id olish
def get_contact_id_from_deal(deal_id):
    url = BITRIX_WEBHOOK + "crm.deal.get.json"
    response = requests.get(url, params={"id": deal_id})
    data = response.json()

    return data.get("result", {}).get("CONTACT_ID")


# 👉 Contactdan telefon olish
def get_contact_phone(contact_id):
    url = BITRIX_WEBHOOK + "crm.contact.get.json"
    response = requests.get(url, params={"id": contact_id})
    data = response.json()

    phones = data.get("result", {}).get("PHONE", [])

    if phones:
        return phones[0]["VALUE"]

    return None


# 👉 Telefonni format qilish
def format_phone(phone):
    if not phone:
        return None

    # +998911234567 → 911234567
    if phone.startswith("+998"):
        return phone.replace("+998", "")

    return phone


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    print("RAW DATA:", data)

    deal_id = data.get("deal_id")

    contact_id = get_contact_id_from_deal(deal_id)
    print("CONTACT_ID:", contact_id)

    phone = get_contact_phone(contact_id)
    print("PHONE RAW:", phone)

    formatted_phone = format_phone(phone)
    print("PHONE FORMATTED:", formatted_phone)

    return jsonify({
        "status": "ok",
        "phone": formatted_phone
    })


@app.route("/", methods=["GET"])
def home():
    return "CRM Webhook ishlayapti 🚀"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)