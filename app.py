from flask import Flask, request, jsonify
import requests
import re

app = Flask(__name__)

# 🔑 BITRIX WEBHOOK (o'zingnikini qo'y)
BITRIX_WEBHOOK = "https://derza.bitrix24.kz/rest/1/r1hgjqdeoyhdtx1n/"

# 📌 Telefonni tozalash va formatlash
def format_phone(phone):
    if not phone:
        return None

    # Faqat raqamlarni qoldiramiz
    phone = re.sub(r"\D", "", phone)

    # 998 kodni olib tashlaymiz (agar boshida bo'lsa)
    if phone.startswith("998"):
        phone = phone[3:]

    # Endi phone faqat mahalliy raqam (9 yoki 8 xonali bo'lishi mumkin)

    if len(phone) == 12 and phone.startswith("998"):
        # +998901234567 → 901234567 (998 olib tashlanadi)
        return phone[3:]

    elif len(phone) == 9:
        # 901234567 → 998901234567 (998 qo'shiladi)
        return "998" + phone

    else:
        # Boshqa noto'g'ri formatlar — o'zgartirishsiz qaytaramiz
        print(f"PHONE FORMAT WARNING: kutilmagan uzunlik {len(phone)} → {phone}")
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

    # ❗ 1. Eski telefonlarni tozalaymiz
    requests.post(url, json={
        "id": contact_id,
        "fields": {
            "PHONE": []
        }
    })

    # ❗ 2. Yangi telefonni yozamiz
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

    # 2. Telefonni olamiz
    phone = get_contact_phone(contact_id)
    print("PHONE RAW:", phone)

    if not phone:
        return jsonify({"error": "telefon topilmadi"})

    # 3. Format qilamiz
    formatted = format_phone(phone)
    print("PHONE FORMATTED:", formatted)

    # 4. Yangilaymiz (eski o'chadi)
    update_contact_phone(contact_id, formatted)

    return jsonify({
        "status": "ok",
        "old": phone,
        "new": formatted
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
