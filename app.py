from flask import Flask, request
app = Flask(__name__)
from controllers.bot_engine import process_message


@app.get("/")
def get():
    return {"status":"received"}


@app.post("/webhook")
def webhook():
    req = request.json
    process_message(req)
    return {"status":"received"}


@app.post("/coinbase_webhook")
def coinbase_webhook():
    req = request.json
    return {"status":"received"}

if __name__ == '__main__':
    app.run()