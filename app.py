from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

BITRIX_WEBHOOK = "https://derza.bitrix24.kz/rest/1/bwmu5i9lq63ur1jc/"

def format_phone(phone):
    if not phone:
        return None
    
    phone = str(phone).strip()

    # Faqat Moizvonki (998 bilan boshlangan)
    if phone.startswith("998"):
        return phone[3:]
    
    return phone  # Asteriskga tegmaydi

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    try:
        # GET yoki POST ni qo‘llab-quvvatlaymiz
        if request.method == 'GET':
            phone = request.args.get("phone")
        else:
            data = request.json or {}
            phone = data.get("phone") or data.get("caller") or data.get("from")

        if not phone:
            return jsonify({"error": "phone yo‘q"})

        formatted = format_phone(phone)

        print("Asl:", phone)
        print("Kesilgan:", formatted)

        # 1. Bitrixda qidiramiz
        search = requests.post(
            BITRIX_WEBHOOK + "crm.duplicate.findbycomm.json",
            json={
                "type": "PHONE",
                "values": [formatted]
            }
        ).json()

        print("Search:", search)

        contact_ids = search.get("result", {}).get("CONTACT", [])

        # 2. Agar mavjud bo‘lsa → update
        if contact_ids:
            contact_id = contact_ids[0]

            update = requests.post(
                BITRIX_WEBHOOK + "crm.contact.update.json",
                json={
                    "id": contact_id,
                    "fields": {
                        "PHONE": [{"VALUE": formatted, "VALUE_TYPE": "WORK"}]
                    }
                }
            )

            print("UPDATE:", update.text)

            return jsonify({"status": "updated", "contact_id": contact_id})

        # 3. Aks holda → yangi lead yaratamiz
        create = requests.post(
            BITRIX_WEBHOOK + "crm.lead.add.json",
            json={
                "fields": {
                    "TITLE": "Qo‘ng‘iroq",
                    "PHONE": [{"VALUE": formatted, "VALUE_TYPE": "WORK"}]
                }
            }
        )

        print("CREATE:", create.text)

        return jsonify({"status": "created"})

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))