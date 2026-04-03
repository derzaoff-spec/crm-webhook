from flask import Flask, request, jsonify
import requests
import re

app = Flask(__name__)

# 🔑 BITRIX WEBHOOK (o'zingnikini qo'y)
BITRIX_WEBHOOK = "https://derza.bitrix24.kz/rest/1/r1hgjqdeoyhdtx1n/"

# 📌 Telefonni tozalash va kesish
def format_phone(phone):
    if not phone:
        return None

    # faqat raqamlarni qoldiramiz
    phone = re.sub(r"\D", "", phone)

    # 998 yoki +998 ni kesadi
    if phone.startswith("998"):
        phone = phone[3:]

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


# 📌 Telefonni to'liq yangilash (eski o'chadi)
def update_contact_phone(contact_id, phone):
    url = BITRIX_WEBHOOK + "crm.contact.update.json"

    # ❗ 1. eski telefonlarni tozalaymiz
    requests.post(url, json={
        "id": contact_id,
        "fields": {
            "PHONE": []
        }
    })

    # ❗ 2. yangi telefonni yozamiz
    response = requests.post(url, json={
        "id": contact_id,
        "fields": {
            "PHONE": [
                {
                    "VALUE": phone,
                    "VALUE_TYPE": "WORK"
                }
            ]
        }
    })

    print("UPDATE RESPONSE:", response.json())


# 🚀 ASOSIY WEBHOOK
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    print("RAW DATA:", data)

    deal_id = data.get("deal_id")

    if not deal_id:
        return jsonify({"error": "deal_id yo'q"})

    # 1. contact_id olamiz
    contact_id = get_contact_id(deal_id)
    print("CONTACT_ID:", contact_id)

    if not contact_id:
        return jsonify({"error": "contact_id topilmadi"})

    # 2. telefonni olamiz
    phone = get_contact_phone(contact_id)
    print("PHONE RAW:", phone)

    if not phone:
        return jsonify({"error": "telefon topilmadi"})

    # 3. format qilamiz
    formatted = format_phone(phone)
    print("PHONE FORMATTED:", formatted)

    # 4. yangilaymiz (eski o'chadi)
    update_contact_phone(contact_id, formatted)

    return jsonify({
        "status": "ok",
        "old": phone,
        "new": formatted
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)