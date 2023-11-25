from controllers.api_provider import Telegram, Intermediary_Bot
from controllers.utils import timestamp, reformat_message, turn_variable_to_string_in_object,\
    commands, lookup_prices, JsonTool, Local_Cache, get_sale_price
from controllers.payment import Payment
from controllers.database import Users
import json
from dotenv import load_dotenv
load_dotenv()
import os
intermediary_bot_id=os.environ.get('intermediary_bot_id')

def process_message(payload):
    try:
        if payload.get('message'):
            payload = payload['message']
            user_id = payload['chat']['id']
            username = payload['chat']['username']
            message = payload.get("text")

            if str(user_id) == str(intermediary_bot_id):
                payload = JsonTool.decrypt(message)
                user_id = payload['user_id']
                type = payload.get("type")

                if type == "text":
                    text = payload['text']
                    if "our current lookup price list" in text.lower() or "please select which lookup" in text.lower():
                        return

                    if "could not get a successful" in text.lower():
                        Local_Cache.delete("current_session")
                        Local_Cache.delete("last_lookup")

                    message_payload = reformat_message(user_id, text)
                    Telegram.sendmessage(message_payload)
                else:
                    content = payload['content']
                    filename = payload['filename']
                    Telegram.sendfile(user_id, filename, content)

                    Local_Cache.delete("current_session")

                    last_lookup = Local_Cache.get("last_lookup")
                    if not last_lookup:
                        return

                    last_lookup_price = lookup_prices.get(last_lookup)
                    user = Users.find({"id": user_id})
                    new_balance = user['balance'] - last_lookup_price
                    Users.update_one({"id": user_id}, {"$set": {"balance": new_balance}})

                    Local_Cache.delete("last_lookup")

                return

            current_session = Local_Cache.get("current_session")
            if not current_session:
                Local_Cache.set("current_session", user_id, 90)

            if message == "/start":
                check_user = Users.find_one({"id": user_id})
                if not check_user:
                    new_user = {"username": username, "id": user_id, "balance": 0, "total_lookups": 0,
                                "created_at": timestamp(), "last_bot_message":"", "last_bot_message_step": 0, "percentage_bonus": 0 }

                    Users.update_one({"id": new_user['id']}, {"$set": new_user}, upsert=True)


            payloads = commands.get(message)
            if payloads:
                new_payloads = []
                for payload in payloads:
                    reformatted_payload = reformat_message(user_id, payload.get('text'), payload.get('buttons'))
                    reformatted_payload = turn_variable_to_string_in_object(user_id, reformatted_payload)
                    new_payloads.append(reformatted_payload)

                if message == "Start Lookup 🔎":

                    payload = {"user_id": user_id, "type": "text", "text": "Start Lookup 🔎"}
                    response = Intermediary_Bot.sendmessage(user_id, payload)
                    if not response:
                        return

                Telegram.sendmessage(new_payloads)
            else:
                user = Users.find_one({"id": user_id})
                accept_payment_messages = ["💴 Please enter your deposit amount in Chat! Min. Deposit is 10$",
                                           "😖 You cannot deposit less than 10$! It should be 10$ or more",
                                           "😖 You must only enter numbers to begin a deposit! Ex. 10 is 10$"]

                # check if the last flow was make payment
                if user['last_bot_message'] in accept_payment_messages:
                    if message.isdigit():
                        amount = int(message)

                        if amount < 10:
                            message_payload = reformat_message(user_id, "😖 You cannot deposit less than 10$! It should be 10$ or more")
                            Telegram.sendmessage(message_payload)
                        else:
                            # call the coinbase commerce to provide the bitcoin address
                            charge = Coinbase.create_charge(user_id, amount)
                            btc_amount = charge['data']['pricing']['bitcoin']['amount']
                            btc_address = charge['data']['addresses']['bitcoin']

                            message_payload = reformat_message(user_id, f"🎉 Your Unique Deposit has been created! See below.\n\n💴 BTC Address: {btc_address}\n💴 BTC Amount: {btc_amount}\n\n⏳ This Deposit Address will expire in the next 60 minutes counting from now.")
                            Telegram.sendmessage(message_payload)

                    else:
                        message_payload = reformat_message(user_id, "😖 You must only enter numbers to begin a deposit! Ex. 10 is 10$")
                        Telegram.sendmessage(message_payload)

                else:
                    message_payload = {"user_id": user_id, "type":"text", "text": message}
                    Intermediary_Bot.sendmessage(user_id, message_payload)



        elif payload.get("callback_query"):
            payload = payload['callback_query']
            user_id = payload['message']['chat']['id']
            username = payload['message']['chat']['username']
            clicked_button = payload['data']


            if clicked_button == "cancel_lookup":
                message_id = payload['message']['message_id']
                Telegram.deletemessage(user_id, message_id)

                message_payload = reformat_message(user_id, "😑 You have cancelled your lookup request!")
                Telegram.sendmessage(message_payload)

            elif clicked_button == "cancel_deposit":
                message_id = payload['message']['message_id']
                Telegram.deletemessage(user_id, message_id)

                message_payload = reformat_message(user_id, "😑 You have cancelled your balance deposit request!")
                Telegram.sendmessage(message_payload)

            elif lookup_prices.get(clicked_button):
                data_item = lookup_prices.get(clicked_button)

                message_id = payload['message']['message_id']
                Telegram.deletemessage(user_id, message_id)

                user = Users.find_one({"id": user_id})
                price = get_sale_price(clicked_button)

                if user['balance'] < price:
                    message_payload = reformat_message(user_id, f"😖 You do not have enough balance to perform a {data_item['name']}!")
                    Telegram.sendmessage(message_payload)
                else:
                    # forward to other bot
                    Local_Cache.set("last_lookup", clicked_button)
                    payload = {"user_id": user_id, "type":"button", "button": clicked_button}
                    Intermediary_Bot.sendmessage(user_id, payload)

            else:
                #send it to the other bot
                payload = {"user_id":user_id, "type":"button", "data": clicked_button}
                Intermediary_Bot.sendmessage(user_id, payload)

    except Exception as e:
        print(e)

