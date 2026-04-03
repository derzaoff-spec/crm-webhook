import requests

url = "https://moizvonki.ru/api/v1"

data = {
    "user_name": "derzaoff@gmail.com",
    "api_key": "4qmz6lkk0woac488c9yvt53wuzpa9qdz",
    "action": "webhook.subscribe",
    "hooks": {
        "call.start": "https://crm-webhook-production.up.railway.app/webhook",
        "call.answer": "https://crm-webhook-production.up.railway.app/webhook",
        "call.finish": "https://crm-webhook-production.up.railway.app/webhook"
    }
}

response = requests.post(url, json=data)

print("Status:", response.status_code)
print("Response:", response.text)