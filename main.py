from flask import Flask, request
app = Flask(__name__)
from controllers.bot_engine import process_message
from controllers.database import Users, Transactions
from controllers.utils import reformat_message, get_parmalink
from controllers.api_provider import Telegram
from threading import Thread

from dotenv import load_dotenv
load_dotenv()
import os

notification_telegram_id = os.getenv("notification_telegram_id")



@app.get("/")
def get():
    return {"status":"received"}


@app.post("/webhook")
def webhook():
    req = request.json
    process_message(req)
    return {"status":"received"}


@app.post("/payment_webhook")
def coinbase_webhook():
    try:
        req = request.json
        transaction_id = req['id']
        amount = req['amount']
        user_id = req['user_id']

        check_transaction = Transactions.find_one({"id": transaction_id})
        if check_transaction:
            return {"message":"transaction already processed"}

        user = Users.find_one({"id": user_id})
        new_balance = int(user['balance']) + int(amount)
        Users.update_one({"id": user_id}, {"$set": {"balance": new_balance}})
        text = f"💸 Success! You just deposited {amount}$ to your Account Balance, Thank You."
        message = reformat_message(user_id, text)
        Telegram.sendmessage(message)
        Transactions.insert_one(req)

        user_link = get_parmalink(user_id, user_id, "profile")
        notification_message = f"user named {user_link} deposited {amount}$ \n\naddress: {req['address']} \ncurrency: {req['currency']}"
        notification_message = reformat_message(notification_telegram_id, notification_message, permalink=True)
        Telegram.sendmessage(notification_message)
    except Exception as e:
        print(e)

    return {"status":"success", "message":"transaction recieved"}


if __name__ == '__main__':
    app.run(port=4000)

