from datetime import datetime, timezone, timedelta
from controllers.database import Users
from cryptography.fernet import Fernet
from dotenv import load_dotenv
load_dotenv()
import json, re, pytz, time, os, boto3
additional_percentage = os.environ.get('additional_percentage')



def timestamp():
    return datetime.utcnow().isoformat()

def reformat_message(chat_id, text, buttons=None):
    payload = {'chat_id': chat_id, 'text': text}
    if buttons:
        payload['reply_markup'] = buttons
    return payload



def convert_utc_to_custom_format(utc_time_str, output_format="%m/%d/%Y %I:%M:%S %p"):
    # Parse UTC time string into a datetime object
    utc_time = datetime.strptime(utc_time_str, "%Y-%m-%dT%H:%M:%S.%f")

    # Set UTC timezone
    utc_timezone = pytz.timezone("UTC")
    utc_time = utc_timezone.localize(utc_time)

    # Convert to the desired output format
    formatted_time = utc_time.strftime(output_format)

    return formatted_time

def turn_variable_to_string_in_message(id, message):

    user = Users.find_one({"id": id}, {"_id": 0})
    if not user:
        return message

    variables = user
    variables['created_at'] = convert_utc_to_custom_format(variables['created_at'])

    if not variables:
        return message

    for key, value in variables.items():
        message = message.replace("{{" + key + "}}", str(value))

    return re.sub(r"{{\w+}}", " ", message)



def turn_variable_to_string_in_object(id, obj):
    pattern = "{{\w+}}"
    match = re.search(pattern, str(obj))
    if not match:
        print("no matching")
        return obj

    def traverse(obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, (dict, list)):
                    traverse(value)
                else:
                    if isinstance(value, str):
                        obj[key] = turn_variable_to_string_in_message(id, value)
        elif isinstance(obj, list):
            for i in range(len(obj)):
                if isinstance(obj[i], (dict, list)):
                    traverse(obj[i])
                else:
                    obj[i] = turn_variable_to_string_in_message(id, str(obj[i]))
        return obj

    return traverse(obj)



class SimpleCache:
    def __init__(self):
        self.cache = {}

    def get(self, key):
        if key in self.cache:
            value, expiry_time = self.cache[key]
            if expiry_time is None or time.time() < expiry_time:
                return value
            else:
                del self.cache[key]
        return None

    def set(self, key, value, expiry_seconds=None):
        expiry_time = None
        if expiry_seconds is not None:
            expiry_time = time.time() + expiry_seconds
        self.cache[key] = (value, expiry_time)

    def delete(self, key):
        if key in self.cache:
            del self.cache[key]


Local_Cache = SimpleCache()


class JsonTool:
    key = "ck-VyswViKa3_O4lCVbSs7Ecvqesw2995Necf0r_XhM="

    @staticmethod
    def encrypt(json_data):
        # Convert JSON to bytes
        json_bytes = json.dumps(json_data).encode('utf-8')

        # Create a Fernet cipher object with the key
        cipher = Fernet(JsonTool.key)

        # Encrypt the bytes
        encrypted_data = cipher.encrypt(json_bytes)

        # Convert the encrypted bytes to a string
        encrypted_str = str(encrypted_data)

        return encrypted_str

    @staticmethod
    def decrypt(encrypted_str):
        # Convert the encrypted string back to bytes
        encrypted_data = eval(encrypted_str)

        # Create a Fernet cipher object with the key
        cipher = Fernet(JsonTool.key)

        # Decrypt the bytes
        decrypted_data = cipher.decrypt(encrypted_data)

        # Convert bytes back to JSON
        decrypted_json = json.loads(decrypted_data.decode('utf-8'))

        return decrypted_json



lookup_prices = {
    "mvr_lookup": {"price": 50, "name": "MVR Lookup"},
    "ssn_lookup": {"price": 10, "name": "SSN Lookup"},
    "dob_lookup": {"price": 12, "name": "SSN+DOB Lookup"},
    "dl_lookup": {"price": 10, "name": "DL Lookup"},
    "dl2_lookup": {"price": 10, "name": "DL2 Lookup"},
    "bdob_lookup": {"price": 5, "name": "DOB Lookup"},
    "verk_lookup": {"price": 15, "name": "DOB/VIN/DL/CAR/LICENSE PLATE Lookup"},
    "prolic_lookup": {"price": 8, "name": "Professional License Lookup"},
    "cs_lookup": {"price": 5, "name": "Credit Score Lookup"},
    "ein_lookup": {"price": 8, "name": "Business Lookup"},
    "phone_lookup": {"price": 8, "name": "Phone Lookup"},
    "ssn_reverse": {"price": 8, "name": "Reverse SSN"},
    "phone_reverse": {"price": 8, "name": "Reverse Phone"},
    "address_reverse": {"price": 8, "name": "Reverse Address"},
    "email_reverse": {"price": 8, "name": "Reverse E-Mail"}
}


start_p = [
    {"text": "👋 Hey {{username}}! A Menu should appear if not please type /start", "buttons": {"resize_keyboard": True, "keyboard": [
        [{"text": "Start Lookup 🔎"}], [{"text": "My Balance 💰"}, {"text": "Deposit Balance 💵"}],
        [{"text": "My Account ⚙️"}, {"text": "Support ℹ️"}]]}}]

def get_sale_price(item):
    org_price = lookup_prices[item]['price']
    percentage = int(additional_percentage)/100 + 1
    new_price = org_price * percentage
    rounded_price = round(new_price, 2)

    if rounded_price.is_integer():
        rounded_price = int(rounded_price)

    return rounded_price



start_lookup_p = [
    {"text": f"💸 Our Current Lookup Price List:\n\n🔎 SSN: {get_sale_price('ssn_lookup')}$\n🔎 SSN & DOB: {get_sale_price('dob_lookup')}$\n🔎 DL: {get_sale_price('dl_lookup')}$\n🔎 DOB/VIN/DL/CAR/LICENSE PLATE: {get_sale_price('verk_lookup')}$\n🔎 Phone: {get_sale_price('phone_lookup')}$\n🔎 DL2: {get_sale_price('dl2_lookup')}$\n🔎 DOB: {get_sale_price('bdob_lookup')}$\n🔎 MVR: {get_sale_price('mvr_lookup')}$ | PA, NH, WA MVR are NOT Instant!\n🔎 CS: {get_sale_price('cs_lookup')}$\n🔎 Professional License Lookup: {get_sale_price('prolic_lookup')}$\n🔎 Business Lookup: {get_sale_price('ein_lookup')}$\n⚡️ Reverse SSN: {get_sale_price('ssn_reverse')}$\n⚡️ Reverse Phone: {get_sale_price('phone_reverse')}$\n⚡️ Reverse Address: {get_sale_price('address_reverse')}$\n⚡️ Reverse E-Mail: {get_sale_price('email_reverse')}$"},

    {"text": "👋 Hey {{username}}! Please select which Lookup you want to start",
     "buttons": {'inline_keyboard': [
        [
            {"text": "🔎 MVR Lookup", "callback_data":"mvr_lookup"},
            {"text": "🔎 SSN Lookup", "callback_data":"ssn_lookup"},
            {"text": "🔎 SSN+DOB Lookup", "callback_data": "dob_lookup"}
        ],
        [
            {"text": "🔎 DL Lookup", "callback_data":"dl_lookup"},
            {"text": "🔎 DL2 Lookup", "callback_data":"dl2_lookup"},
            {"text": "🔎 DOB Lookup", "callback_data":"bdob_lookup"}
        ],
        [
            {"text": "🔎 DOB/VIN/DL/CAR/LICENSE PLATE Lookup", "callback_data":"verk_lookup"},
            {"text": "🔎 Professional License Lookup", "callback_data": "prolic_lookup"}
        ],
        [
            {"text": "↙️ Other Lookups ↘️", "callback_data": "other_lookup"}
        ],
        [
            {"text": "🔎 Credit Score Lookup", "callback_data": "cs_lookup"}
        ],
        [
            {"text": "🔎 Business Lookup", "callback_data": "ein_lookup"},
            {"text": "🔎 Phone Lookup", "callback_data": "phone_lookup"}

        ],
        [
             {"text": "️⚡️ Reverse SSN", "callback_data":"ssn_reverse"},
             {"text": "️⚡️ Reverse Phone", "callback_data": "phone_reverse"}
        ],
        [
            {"text": "⚡️ Reverse Address", "callback_data":"address_reverse"},
            {"text": "⚡️ Reverse E-Mail", "callback_data":"email_reverse"}
        ],
        [
             {"text": "❌ Cancel Lookup", "callback_data": "cancel_lookup"}
        ]
    ],

 }
     }]



my_balance_p = [{"text": "💸 {{username}}'s Balance 💸\n\n💵 Current Account Balance: {{balance}}$\n🈹 Current Balance Bonus: {{percentage_bonus}}%"}]

my_account_p = [{"text": "🔥 {{username}}'s Account 🔥\n\n⚙️ My User Id: {{id}}\n🔎 My Total Lookups: {{total_lookups}}\n❤️ My First Visit: {{created_at}}\n💸 My Balance: {{balance}}$"}]

deposit_p = [{"text":"💴 Please enter your deposit amount in Chat! Min. Deposit is 10$",
              "buttons": {'inline_keyboard': [
        [{'text': '❌ Cancel Deposit', 'callback_data': 'cancel_deposit'}],

    ],
}
}]


support_p = [{"text": "💬 Support Contacts 💬\n\nℹ️ You may reach us under the following tags:\n@StealthwayDeskSupport\n\nℹ️ Our Official Telegram Channel:\n@stealthwayshopfeedback"}]


commands = {"/start": start_p, "Start Lookup 🔎": start_lookup_p, "My Balance 💰": my_balance_p, "My Account ⚙️": my_account_p, "Deposit Balance 💵": deposit_p, "Support ℹ️": support_p}

