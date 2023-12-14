from controllers.api_provider import Telegram, Intermediary_Bot
from controllers.utils import timestamp, reformat_message, turn_variable_to_string_in_object,\
    commands, lookup_prices, JsonTool, Local_Cache, get_sale_price, get_parmalink
from controllers.payment import Payment
from controllers.database import Users
import json
from dotenv import load_dotenv
load_dotenv()
import os

intermediary_username = os.getenv("intermediary_username")
notification_telegram_id = os.getenv("notification_telegram_id")
admin_userid=os.getenv("admin_userid")

def is_intermediary(user_id):
    intermediary_user_id = Local_Cache.get("intermediary_user_id")
    if intermediary_user_id == user_id:
        return True

    user = Users.find_one({"id": user_id})
    if user and user['username'] == intermediary_username:
        Local_Cache.set("intermediary_user_id", user_id)
        return True

    return False



def process_message(payload):
    try:
        if payload.get('message'):
            payload = payload['message']
            user_id = payload['chat']['id']
            username = payload['chat']['username']
            message = payload.get("text")

            # if is a group do not work
            if str(user_id) == str(notification_telegram_id):
                return

            if str(username) == str(intermediary_username):
                payload = JsonTool.decrypt(message)

                if payload:
                    user_id = payload['user_id']
                    type = payload.get("type")

                    if type == "text":
                        text = payload['text']

                        buttons = None
                        if payload.get("buttons"):
                            buttons = {'inline_keyboard': payload.get("buttons")}

                        ignore_lists = ["our current lookup price list", "please select which lookup", "just deposited",
                                         "account balance", "please select a payment method", "my balance", "have cancelled your lookup"]

                        if "not have enough balance" in text.lower():
                            message_payload = reformat_message(user_id, "Please bear with us, Our system is currently undergoing maintenance")
                            Telegram.sendmessage(message_payload)

                            notification_message = f"Our bot is currently low on funds"
                            notification_message = reformat_message(notification_telegram_id, notification_message)
                            Telegram.sendmessage(notification_message)

                            return

                        for ig in ignore_lists:
                            if ig.lower() in text.lower():
                                return

                        if "could not get a successful" in text.lower():
                            Local_Cache.delete("current_session")

                        message_payload = reformat_message(user_id, text, buttons)
                        Telegram.sendmessage(message_payload)
                    else:
                        content = payload['content']
                        filename = payload['filename']
                        Telegram.sendfile(user_id, filename, content)

                        Local_Cache.delete("current_session")

                        user = Users.find_one({"id": user_id})

                        last_lookup = user.get("last_lookup")
                        if not last_lookup:
                            return

                        last_lookup_price = lookup_prices.get(last_lookup)
                        new_balance = user['balance'] - last_lookup_price

                        new_total_lookups = user['total_lookups'] + 1

                        Users.update_one({"id": user_id}, {"$set": {"balance": new_balance, "total_lookups": new_total_lookups}})
                else:
                    # the message is a comamnd
                    # admin_commands = ["withdraw", "check_address_with_funds"]
                    if message == "/withdraw":
                        Payment.withdraw()
                        message = reformat_message(user_id, "Funds withdrawn")
                        Telegram.sendmessage(message)
                    elif message == "/balance":
                        message = Payment.balance()
                        message = reformat_message(user_id, message)
                        Telegram.sendmessage(message)
                    else:
                        message = reformat_message(user_id, "Invalid command")
                        Telegram.sendmessage(message)



                #check if the intermediary bot detail exist on the server, if not save it
                check_user = Users.find_one({"id": user_id})
                if not check_user:
                    new_user = {"username": username, "id": user_id, "balance": 0, "total_lookups": 0,
                                "created_at": timestamp(), "last_bot_message":"", "last_bot_message_step": 0, "percentage_bonus": 0 }

                    Users.update_one({"id": new_user['id']}, {"$set": new_user}, upsert=True)

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


                user_link = get_parmalink(user_id, user_id, "profile")
                notification_message = f"user with id {user_link} started the bot"
                notification_message = reformat_message(notification_telegram_id, notification_message, permalink=True)
                Telegram.sendmessage(notification_message)


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
                accept_payment_messages = ["💴 Please enter your deposit amount in Chat! Min. Deposit is 10$", #"💴 Please enter your deposit amount in Chat! Min. Deposit is 10$
                                          "😖 You cannot deposit less than 10$! It should be 10$ or more", #"😖 You cannot deposit less than 10$! It should be 10$ or more",
                                           "😖 You must only enter numbers to begin a deposit! Ex. 10 is 10$"] # "😖 You must only enter numbers to begin a deposit! Ex. 10 is 10$"

                # check if the last flow was make payment
                if user['last_bot_message'] in accept_payment_messages:
                    if message.isdigit():
                        amount = int(message)

                        if amount < 1:
                            message_payload = reformat_message(user_id, "😖 You cannot deposit less than 10$! It should be 10$ or more") #😖 You cannot deposit less than 10$! It should be 10$ or more
                            Telegram.sendmessage(message_payload)
                        else:
                            selected_currency = user['selected_currency']
                            charge = Payment.create_charge(user_id, amount, selected_currency)
                            currency = charge['currency']
                            amount = charge['amount']
                            address = charge['address']

                            message_payload = reformat_message(user_id, f"🎉 Your Unique Deposit has been created! See below.\n\n💴 {currency} Address: {address}\n💴 {currency} Amount: {amount}\n\n⏳ This Deposit Address will expire in the next 60 minutes counting from now.")
                            Telegram.sendmessage(message_payload)

                    else:
                        message_payload = reformat_message(user_id, "😖 You must only enter numbers to begin a deposit! Ex. 10 is 10$")
                        Telegram.sendmessage(message_payload)

                else:

                    if str(admin_userid) == str(user_id) and message == "/withdraw":
                        Payment.withdraw()
                        message = reformat_message(user_id, "Funds withdrawn")
                        Telegram.sendmessage(message)
                    elif str(admin_userid) == str(user_id) and  message == "/balance":
                        message = Payment.balance()
                        message = reformat_message(user_id, message)
                        Telegram.sendmessage(message)
                    else:
                        message_payload = {"user_id": user_id, "type": "text", "text": message}
                        Intermediary_Bot.sendmessage(user_id, message_payload)




        elif payload.get("callback_query"):
            payload = payload['callback_query']
            user_id = payload['message']['chat']['id']
            username = payload['message']['chat']['username']
            clicked_button = payload['data']
            message_id = payload['message']['message_id']
            Telegram.deletemessage(user_id, message_id)

            currencies = ["bitcoin", "litecoin", "eth_usdt", "tron_usdt", "ethereum"]

            if clicked_button in currencies:
                Users.update_one({"id": user_id}, {"$set": {"selected_currency": clicked_button}})
                text = "💴 Please enter your deposit amount in Chat! Min. Deposit is 10$" # "💴 Please enter your deposit amount in Chat! Min. Deposit is 10$"
                buttons = {'inline_keyboard':  [
                    [{'text': '❌ Cancel Deposit', 'callback_data': 'cancel_deposit'}],
                ]}

                reformatted_payload = reformat_message(user_id, text, buttons)
                Telegram.sendmessage(reformatted_payload)


            elif clicked_button == "cancel_lookup":
                message_payload = reformat_message(user_id, "😑 You have cancelled your lookup request!")
                Telegram.sendmessage(message_payload)

                payload = {"user_id":user_id, "type":"button", "button": "cancel_lookup"}
                Intermediary_Bot.sendmessage(user_id, payload)

            elif clicked_button == "cancel_deposit":

                message_payload = reformat_message(user_id, "😑 You have cancelled your balance deposit request!")
                Telegram.sendmessage(message_payload)

            elif lookup_prices.get(clicked_button):
                data_item = lookup_prices.get(clicked_button)

                user = Users.find_one({"id": user_id})
                price = get_sale_price(clicked_button)

                if user['balance'] < price:
                    message_payload = reformat_message(user_id, f"😖 You do not have enough balance to perform a {data_item['name']}!")
                    Telegram.sendmessage(message_payload)
                else:
                    # forward to other bot
                    Users.update_one({"id": user_id}, {"$set": {"last_lookup": clicked_button}})
                    payload = {"user_id": user_id, "type":"button", "button": clicked_button}
                    Intermediary_Bot.sendmessage(user_id, payload)

            else:
                #send it to the other bot

                payload = {"user_id":user_id, "type":"button", "button": clicked_button}
                Intermediary_Bot.sendmessage(user_id, payload)

    except Exception as e:
        print(e)
        return
