from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "Server ishlayapti"

@app.route("/webhook", methods=["POST", "GET"])
def webhook():
    try:
        # 🔹 JSON yoki form data olish
        data = request.get_json(silent=True)

        if not data:
            data = request.form.to_dict()

        print("RAW DATA:", data)

        # 🔹 agar list bo‘lsa → fix
        if isinstance(data, list):
            data = data[0]

        # 🔹 phone olish
        phone = None

        if isinstance(data, dict):
            phone = data.get("phone")

        return jsonify({
            "status": "ok",
            "phone": phone,
            "received": data
        })

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({
            "status": "error",
            "message": str(e)
        })

# Railway uchun
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)