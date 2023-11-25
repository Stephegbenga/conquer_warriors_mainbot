from flask import Flask, request
app = Flask(__name__)
from controllers.bot_engine import process_message
from controllers.database import Users
from threading import Thread



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
    req = request.json

    amount = req['amount']
    user_id = req['user_id']

    user = Users.find_one({"id": user_id})
    new_balance = int(user['balance']) + int(amount)
    Users.update_one({"id": user_id}, {"$set": {"balance": new_balance}})

    return {"status":"success", "message":"transaction recieved"}


if __name__ == '__main__':
    app.run(port=4000)

