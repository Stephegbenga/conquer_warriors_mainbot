import json, requests, os
from dotenv import load_dotenv
load_dotenv()

COINBASE_API_KEY = os.environ.get("COINBASE_API_KEY")

class Coinbase:
    @staticmethod
    def create_charge(user_id, user_name, amount):
        url = "https://api.commerce.coinbase.com/charges/"
        payload = json.dumps({
            "name": "50chats",
            "description": "thanks for your payment",
            "pricing_type": "fixed_price",
            "local_price": {
            "amount": amount,
            "currency": 'USD',
            },
            "metadata": {
                "user_id": user_id,
                "user_name": user_name,
                "amount": amount
            },
        })

        headers = {
            'Content-Type': 'application/json',
            'X-CC-Api-Key': COINBASE_API_KEY
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        return response.json()
