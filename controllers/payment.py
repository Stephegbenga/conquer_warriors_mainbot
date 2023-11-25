import json, requests, os
from dotenv import load_dotenv
load_dotenv()

hosted_url=os.environ.get("hosted_url")


class Payment:
    @staticmethod
    def create_charge(user_id, amount, currency):
        url = "https://api.commerce.coinbase.com/charges/"
        payload = json.dumps(
             {
                "user_id": user_id,
                "amount": amount,
                 "currency":currency,
                "endpoint": f"{hosted_url}/payment_webhook"
            })

        headers = {
            'Content-Type': 'application/json'}

        response = requests.request("POST", url, headers=headers, data=payload)
        return response.json()