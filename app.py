from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

BITRIX_WEBHOOK = "https://derza.bitrix24.kz/rest/1/bwmu5i9lq63ur1jc/"

def format_phone(phone):
    if phone and phone.startswith("998"):
        return phone[3:]
    return phone

def find_contact(phone):
    response = requests.post(
        BITRIX_WEBHOOK + "crm.contact.list.json",
        json={
            "filter": {"PHONE": phone},
            "select": ["ID", "NAME"]
        }
    )
    return response.json().get("result", [])

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json

    phone = data.get("phone")

    if not phone:
        return jsonify({"error": "no phone"}), 400

    formatted = format_phone(phone)

    print("Asl:", phone)
    print("Kesilgan:", formatted)

    contacts = find_contact(formatted)

    if contacts:
        contact_id = contacts[0]["ID"]

        # UPDATE (telefonni to‘g‘rilaymiz)
        requests.post(
            BITRIX_WEBHOOK + "crm.contact.update.json",
            json={
                "id": contact_id,
                "fields": {
                    "PHONE": [{"VALUE": formatted, "VALUE_TYPE": "WORK"}]
                }
            }
        )

        return jsonify({"status": "updated", "contact_id": contact_id})

    else:
        # YANGI CONTACT
        response = requests.post(
            BITRIX_WEBHOOK + "crm.contact.add.json",
            json={
                "fields": {
                    "NAME": "Avto kontakt",
                    "PHONE": [{"VALUE": formatted, "VALUE_TYPE": "WORK"}]
                }
            }
        )

        contact_id = response.json().get("result")

        # YANGI DEAL
        requests.post(
            BITRIX_WEBHOOK + "crm.deal.add.json",
            json={
                "fields": {
                    "TITLE": "Qo'ng'iroq",
                    "CONTACT_ID": contact_id
                }
            }
        )

        return jsonify({"status": "created", "contact_id": contact_id})

@app.route('/')
def home():
    return "Server ishlayapti 🚀"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))