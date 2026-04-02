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
    try:
        phone = request.args.get("phone") or request.json.get("phone") if request.is_json else None

        print("Keldi:", phone)

        if not phone:
            return jsonify({"error": "phone yo‘q"})

        formatted = format_phone(phone)

        print("Kesilgan:", formatted)

        # 🔍 1. Dublikat qidirish
        try:
            search = requests.post(
                BITRIX_WEBHOOK + "crm.duplicate.findbycomm.json",
                json={
                    "type": "PHONE",
                    "values": [formatted]
                },
                timeout=5
            ).json()

            print("Search:", search)

        except Exception as e:
            print("Search error:", str(e))
            return jsonify({"error": "search failed"})

        contacts = search.get("result", {}).get("CONTACT", [])

        # 🔄 Agar bor bo‘lsa UPDATE
        if contacts:
            contact_id = contacts[0]
            print("Topildi:", contact_id)

            try:
                requests.post(
                    BITRIX_WEBHOOK + "crm.contact.update.json",
                    json={
                        "id": contact_id,
                        "fields": {
                            "PHONE": [{"VALUE": formatted, "VALUE_TYPE": "WORK"}]
                        }
                    },
                    timeout=5
                )
            except Exception as e:
                print("Update error:", str(e))

            return jsonify({"status": "updated", "id": contact_id})

        # 🆕 Agar yo‘q bo‘lsa CREATE
        else:
            print("Topilmadi → yangi yaratiladi")

            try:
                new_contact = requests.post(
                    BITRIX_WEBHOOK + "crm.contact.add.json",
                    json={
                        "fields": {
                            "NAME": "Qo‘ng‘iroq",
                            "PHONE": [{"VALUE": formatted, "VALUE_TYPE": "WORK"}]
                        }
                    },
                    timeout=5
                ).json()

                print("New:", new_contact)

            except Exception as e:
                print("Create error:", str(e))
                return jsonify({"error": "create failed"})

            return jsonify({"status": "created", "contact": new_contact})

    except Exception as e:
        print("General error:", str(e))
        return jsonify({"error": "server error"})
