from utils import Local_Cache, JsonTool, json
from telethon import TelegramClient, events, functions, types
from flask import Flask
import os, boto3
from uuid import uuid4
from dotenv import load_dotenv
from threading import Thread
load_dotenv()

app = Flask(__name__)

api_id = os.environ.get("api_id")
api_hash = os.environ.get("api_hash")
phone = os.environ.get("phone")
mainbot_server = os.environ.get("mainbot_server")
mainbot_username = os.environ.get("mainbot_username")

client = TelegramClient(phone, api_id, api_hash)

aws_access_key = os.getenv('aws_access_key')
aws_secret_key = os.getenv('aws_secret_key')
aws_region = os.getenv('aws_region')
queue_url = os.getenv('queue_url')


sqs = boto3.client('sqs', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key, region_name=aws_region)

class Sqs:

    @staticmethod
    def sendmessage(payload):
        sqs.set_queue_attributes(QueueUrl=queue_url, Attributes={'ContentBasedDeduplication': 'true'})
        payload['sender'] = "intermediary_bot"
        message_group_id = uuid4().hex

        message = json.dumps(payload)

        response = sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=message,
            MessageGroupId=message_group_id
        )

        print(f"MessageId: {response['MessageId']}")


    @staticmethod
    async def watch_queue():
        while True:
            try:
                response = sqs.receive_message(QueueUrl=queue_url, AttributeNames=['All'], MaxNumberOfMessages=1,
                                               MessageAttributeNames=['All'], VisibilityTimeout=10, WaitTimeSeconds=20)

                if 'Messages' in response:
                    for message in response['Messages']:
                        receipt_handle = message['ReceiptHandle']
                        payload = json.loads(message['Body'])
                        await main_bot_handler(payload)
                        try:
                            sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=receipt_handle)
                        except Exception as e:
                            print("Error deleting message:", e)
                else:
                    print("No messages received. Retrying...")


            except Exception as e:
                print(f"Error: {str(e)}")
                pass





@client.on(events.NewMessage(chats=["stealthwaylookup_bot"]))
async def handler(event):
    try:
        if event.media and isinstance(event.media, types.MessageMediaDocument):
            document = event.media.document
            file_name = document.attributes[0].file_name  # Get the file name

            await client.download_media(event.media, file=file_name)

            mime_type = document.mime_type

            if mime_type != "text/plain":
                return

            with open(file_name, 'r', encoding='utf-8') as file:
                txt_content = file.read()

            file.close()
            os.remove(file_name)

            payload = {"type": "file", "filename": file_name, "content": txt_content}

        else:
            buttons_data = []
            if event.message.reply_markup:
                print("reached here ====")
                current_session = Local_Cache.get("current_session")
                user_id = current_session['user_id']
                Local_Cache.set(f"last_peer_message_{user_id}", {"peer_id": event.message.peer_id, "message_id": event.message.id})

            payload = {"type": "text", "text": event.raw_text}

        current_session = Local_Cache.get("current_session")
        if not current_session:
            return

        payload['user_id'] = current_session['user_id']
        Sqs.sendmessage(payload)

    except Exception as e:
        print(e, "")


async def main_bot_handler(payload):
    print(payload)
    try:
        if payload['sender'] == "intermediary_bot":
            return

        Local_Cache.set("current_session", payload)

        if payload['type'] == "text":
            await client.send_message("stealthwaylookup_bot", payload['text'])
        else:
            button_data = b'' + payload['button'].encode('utf-8')

            last_peer_message = Local_Cache.get(f"last_peer_message_{payload['user_id']}")

            await client(
                functions.messages.GetBotCallbackAnswerRequest(last_peer_message['peer_id'], last_peer_message['message_id'],
                                                               data=button_data))

    except Exception as e:
        print(e)



Thread(target=Sqs.watch_queue).start()

client.start()
client.run_until_disconnected()







