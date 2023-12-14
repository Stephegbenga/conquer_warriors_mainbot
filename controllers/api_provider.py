import requests
from controllers.database import Users
from controllers.utils import JsonTool, reformat_message, Local_Cache
from dotenv import load_dotenv
load_dotenv()
import os, json

bot_token = os.environ.get('bot_token')
intermediary_username = os.environ.get('intermediary_username')


class Telegram:
    base_url = f"https://api.telegram.org/bot{bot_token}"

    @staticmethod
    def setwebhook(url):
        payload = {"url": url}
        response = requests.post(f"{Telegram.base_url}/setWebhook", json=payload)
        print(response.json())

    @staticmethod
    def sendmessage(data):
        if isinstance(data, list):
            for payload in data:
                response = requests.post(f"{Telegram.base_url}/sendMessage", json=payload)

            for payload in data:
                Users.update_one({"id": payload['chat_id']}, {"$set":{"last_bot_message": payload['text']}})
        else:
            response = requests.post(f"{Telegram.base_url}/sendMessage", json=data)
            print(response.json())
            Users.update_one({"id": data['chat_id']}, {"$set": {"last_bot_message": data['text']}})


    @staticmethod
    def deletemessage(chat_id, msg_id):
        payload = {'chat_id': chat_id, 'message_id': msg_id}
        response = requests.post(f"{Telegram.base_url}/deleteMessage", json=payload)
        print(response.json())


    @staticmethod
    def sendfile(user_id, file_path, content):
        payload = {"chat_id": user_id}

        with open(file_path, 'w') as file:
            file.write(content)

        file.close()
        with open(file_path, 'rb') as file:
            files = {'document': (file_path, file.read())}

        response = requests.post(f"{Telegram.base_url}/sendDocument", params=payload, files=files)
        print(response.json())

        file.close()
        os.remove(file_path)


class Intermediary_Bot:
    base_url = f"https://api.telegram.org/bot{bot_token}"

    @staticmethod
    def sendmessage(user_id, data):
        current_session = Local_Cache.get("current_session")

        if str(current_session) != str(user_id) and current_session:
            message_payload = reformat_message(user_id, "Please try again in 2 minutes!")
            Telegram.sendmessage(message_payload)
            return

        message = JsonTool.encrypt(data)

        intermediary_user = Users.find_one({"username": intermediary_username})
        if not intermediary_user:
            return
        chat_id = intermediary_user['id']

        payload = reformat_message(chat_id, message)

        response = requests.post(f"{Telegram.base_url}/sendMessage", json=payload)
        print(response.json)
        return True


