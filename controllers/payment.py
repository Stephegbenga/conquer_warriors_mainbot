import json, requests, os
from dotenv import load_dotenv
from uuid import uuid4

load_dotenv()

hosted_url=os.environ.get("hosted_url")
payment_processor_url=os.environ.get("payment_processor_url")



class Payment:
    @staticmethod
    def create_charge(user_id, amount, currency):
        url = f"{payment_processor_url}/charge"

        unique_id = str(uuid4()).replace("-", "")

        payload = json.dumps(
             {
                 "id": unique_id,
                "user_id": user_id,
                "amount": amount,
                "currency":currency,
                "endpoint": "http://localhost:4000/payment_webhook"
            })

        headers = {
            'Content-Type': 'application/json'}

        response = requests.request("POST", url, headers=headers, data=payload)
        return response.json()


    @staticmethod
    def withdraw():
        url = f"{payment_processor_url}/withdraw"
        headers = {
            'Content-Type': 'application/json'}
        response = requests.request("GET", url, headers=headers)
        print(response.json())


    @staticmethod
    def balance():
        url = f"{payment_processor_url}/balance"
        headers = {
            'Content-Type': 'application/json'}
        response = requests.request("GET", url, headers=headers).json()
        return response['message']
