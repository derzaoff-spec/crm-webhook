from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# 🔥 BU SENING BITRIX WEBHOOK
BITRIX_WEBHOOK = "https://derza.bitrix24.kz/rest/1/r1hgjqdeoyhdtx1n/"

# 📌 Telefonni kesish
def format_phone(phone):
    if phone.startswith("+998"):
        return phone[4:]
    return phone

# 📌 Deal orqali contact_id olish
def get_contact_id(deal_id):
    url = BITRIX_WEBHOOK + "crm.deal.get.json"
    response = requests.get(url, params={"id": deal_id}).json()

    return response["result"].get("CONTACT_ID")

# 📌 Contactdan telefon olish
def get_contact_phone(contact_id):
    url = BITRIX_WEBHOOK + "crm.contact.get.json"
    response = requests.get(url, params={"id": contact_id}).json()

    phones = response["result"].get("PHONE", [])
    if phones:
        return phones[0]["VALUE"]

    return None

# 📌 Contactni update qilish
def update_contact_phone(contact_id, phone):
    url = BITRIX_WEBHOOK + "crm.contact.update.json"

    data = {
        "id": contact_id,
        "fields": {
            "PHONE": [
                {
                    "VALUE": phone,
                    "VALUE_TYPE": "WORK"
                }
            ]
        }
    }

    response = requests.post(url, json=data)
    print("UPDATE RESPONSE:", response.json())


# 🚀 ASOSIY WEBHOOK
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    print("RAW DATA:", data)

    deal_id = data.get("deal_id")

    if not deal_id:
        return jsonify({"error": "no deal_id"})

    # 1. contact_id olamiz
    contact_id = get_contact_id(deal_id)
    print("CONTACT_ID:", contact_id)

    if not contact_id:
        return jsonify({"error": "no contact_id"})

    # 2. phone olamiz
    phone = get_contact_phone(contact_id)
    print("PHONE RAW:", phone)

    if not phone:
        return jsonify({"error": "no phone"})

    # 3. format qilamiz
    formatted = format_phone(phone)
    print("PHONE FORMATTED:", formatted)

    # 4. BITRIXGA QAYTA YOZAMIZ 🔥
    update_contact_phone(contact_id, formatted)

    return jsonify({
        "status": "ok",
        "phone_before": phone,
        "phone_after": formatted
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)