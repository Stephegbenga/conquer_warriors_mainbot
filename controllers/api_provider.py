import requests
bot_token = "6083717950:AAFk6XbfotFmaKyXSkDNGdTlw9N9rbYrq50"


class Telegram:
    base_url = f"https://api.telegram.org/bot{bot_token}"

    @staticmethod
    def setwebhook(url):
        payload = {"url": url}
        response = requests.post(f"{Telegram.base_url}/setWebhook", json=payload)
        print(response.json())

    @staticmethod
    def sendmessage(payload):
        response = requests.post(f"{Telegram.base_url}/sendMessage", json=payload)
        print(response.json())

    @staticmethod
    def deletemessage(chat_id, msg_id):
        payload = {'chat_id': chat_id, 'message_id': msg_id}
        response = requests.post(f"{Telegram.base_url}/deleteMessage", json=payload)
        print(response.json())

