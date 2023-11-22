from controllers.api_provider import Telegram
from controllers.utils import timestamp, reformat_message, turn_variable_to_string_in_object, commands, lookup_prices
from controllers.database import Users


def process_message(payload):

    if payload.get('message'):
        payload = payload['message']
        user_id = payload['chat']['id']
        message = payload.get("text")

        if message == "/start":
            check_user = Users.find_one({"id": user_id})
            if not check_user:
                print(timestamp())
                new_user = {"username": payload['chat']['username'], "id": user_id, "balance": 0, "total_lookups": 0,
                            "created_at": timestamp(), "last_message":"", "last_message_step": 0, "percentage_bonus": 0 }

                Users.update_one({"id": new_user['id']}, {"$set": new_user}, upsert=True)

        payloads = commands.get(message)
        if payloads:
            for payload in payloads:
                reformatted_payload = reformat_message(user_id, payload.get('text'), payload.get('buttons'))
                reformatted_payload = turn_variable_to_string_in_object(user_id, reformatted_payload)
                Telegram.sendmessage(reformatted_payload)
        else:
            # send to the other bot
            pass


    elif payload.get("callback_query"):
        payload = payload['callback_query']
        user_id = payload['message']['chat']['id']
        clicked_button = payload['data']

        if clicked_button == "cancel_lookup":
            message_id = payload['message']['message_id']
            Telegram.deletemessage(user_id, message_id)

            message_payload = reformat_message(user_id, "😑 You have cancelled your lookup request!")
            Telegram.sendmessage(message_payload)

        elif lookup_prices.get(clicked_button):
            data_item = lookup_prices.get(clicked_button)

            message_id = payload['message']['message_id']
            Telegram.deletemessage(user_id, message_id)

            user = Users.find_one({"id": user_id})

            if user['balance'] < data_item['price']:
                message_payload = reformat_message(user_id, f"😖 You do not have enough balance to perform a {data_item['name']}!")
                Telegram.sendmessage(message_payload)
            else:
                pass


        else:
            return




