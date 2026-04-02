from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

BITRIX_WEBHOOK = "https://derza.bitrix24.kz/rest/1/bwmu5i9lq63ur1jc/"

def format_phone(phone):
    if phone and phone.startswith("998"):
        return phone[3:]
    return phone

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    phone = request.args.get("phone")

    print("Keldi:", phone)

    if not phone:
        return jsonify({"error": "phone yo‘q"})

    formatted = format_phone(phone)

    print("Kesilgan:", formatted)

    # 🔍 1. DUBLIKATNI QIDIRAMIZ
    search = requests.post(
        BITRIX_WEBHOOK + "crm.duplicate.findbycomm.json",
        json={
            "type": "PHONE",
            "values": [formatted]
        }
    ).json()

    print("Search:", search)

    contacts = search.get("result", {}).get("CONTACT", [])

    if contacts:
        contact_id = contacts[0]
        print("Topildi:", contact_id)

        # ✏️ UPDATE (kontaktga yozamiz)
        requests.post(
            BITRIX_WEBHOOK + "crm.contact.update.json",
            json={
                "id": contact_id,
                "fields": {
                    "PHONE": [{"VALUE": formatted, "VALUE_TYPE": "WORK"}]
                }
            }
        )

        return jsonify({"status": "updated"})

    else:
        print("Topilmadi → yangi yaratiladi")

        # 🆕 YANGI KONTAKT
        new_contact = requests.post(
            BITRIX_WEBHOOK + "crm.contact.add.json",
            json={
                "fields": {
                    "NAME": "Qo‘ng‘iroq",
                    "PHONE": [{"VALUE": formatted, "VALUE_TYPE": "WORK"}]
                }
            }
        ).json()

        return jsonify({"status": "created", "contact": new_contact})

import os
app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))