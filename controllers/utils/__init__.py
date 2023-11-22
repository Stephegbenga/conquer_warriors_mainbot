from datetime import datetime, timezone, timedelta
from controllers.database import Users
import re
import pytz

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



lookup_prices = {
    "mvr_lookup": {"price": 50, "name": ""},
    "ssn_lookup": {"price": 10, "name": ""},
    "ssn_dob_lookup": {"price": 12, "name": ""},
    "dl_lookup": {"price": 10, "name": ""},
    "dl2_lookup": {"price": 10, "name": ""},  # Fix the typo here
    "dob_lookup": {"price": 5, "name": ""},
    "dob_vin_lic_pla_lookup": {"price": 15, "name": ""},
    "professional_license_lookup": {"price": 8, "name": ""},
    "credit_score_lookup": {"price": 5, "name": ""},
    "business_lookup": {"price": 8, "name": ""},
    "phone_lookup": {"price": 8, "name": ""},
    "reverse_ssn": {"price": 8, "name": ""},
    "reverse_phone": {"price": 8, "name": ""},
    "reverse_address": {"price": 8, "name": ""},
    "reverse_email": {"price": 8, "name": ""}
}


start_p = [
    {"text": "👋 Hey {{username}}! A Menu should appear if not please type /start", "buttons": {"resize_keyboard": True, "keyboard": [
        [{"text": "Start Lookup 🔎"}], [{"text": "My Balance 💰"}, {"text": "Deposit Balance 💵"}],
        [{"text": "My Account ⚙️"}, {"text": "Support ℹ️"}]]}}]

start_lookup_p = [
    {"text": "💸 Our Current Lookup Price List:\n\n🔎 SSN: 10$\n🔎 SSN & DOB: 12$\n🔎 DL: 10$\n🔎 DOB/VIN/DL/CAR/LICENSE PLATE: 15$\n🔎 Phone: 8$\n🔎 DL2: 10$\n🔎 DOB: 5$\n🔎 MVR: 50$ | PA, NH, WA MVR are NOT Instant!\n🔎 CS: 5$\n🔎 Professional License Lookup: 8$\n🔎 Business Lookup: 8$\n⚡️ Reverse SSN: 8$\n⚡️ Reverse Phone: 8$\n⚡️ Reverse Address: 8$\n⚡️ Reverse E-Mail: 8$"},

    {"text": "👋 Hey {{username}}! Please select which Lookup you want to start",
     "buttons": {'inline_keyboard': [
        [
            {"text": "🔎 MVR Lookup", "callback_data":"mvr_lookup"},
            {"text": "🔎 SSN Lookup", "callback_data":"ssn_lookup"},
            {"text": "🔎 SSN+DOB Lookup", "callback_data": "ssn_dob_lookup"}
        ],
        [
            {"text": "🔎 DL Lookup", "callback_data":"dl_lookup"},
            {"text": "🔎 DL2 Lookup", "callback_data":"dl2_lookup"},
            {"text": "🔎 DOB Lookup", "callback_data":"dob_lookup"}
        ],
        [
            {"text": "🔎 DOB/VIN/DL/CAR/LICENSE PLATE Lookup", "callback_data":"dob_vin_lic_pla_lookup"},
            {"text": "🔎 Professional License Lookup", "callback_data": "professional_license_lookup"}
        ],
        [
            {"text": "↙️ Other Lookups ↘️", "callback_data": "other_lookup"}
        ],
        [
            {"text": "🔎 Credit Score Lookup", "callback_data": "credit_score_lookup"}
        ],
        [
            {"text": "🔎 Business Lookup", "callback_data": "business_lookup"},
            {"text": "🔎 Phone Lookup", "callback_data": "phone_lookup"}

        ],
        [
             {"text": "️⚡️ Reverse SSN", "callback_data":"reverse_ssn"},
             {"text": "️⚡️ Reverse Phone", "callback_data": "reverse_phone"}
        ],
        [
            {"text": "⚡️ Reverse Address", "callback_data":"reverse_address"},
            {"text": "⚡️ Reverse E-Mail", "callback_data":"reverse_email"}
        ],
        [
             {"text": "❌ Cancel Lookup", "callback_data": "cancel_lookup"}
        ]
    ],

     }}]



my_balance_p = [
    {"text": "💸 {{username}}'s Balance 💸\n\n💵 Current Account Balance: {{balance}}$\n🈹 Current Balance Bonus: {{percentage_bonus}}%"}]
my_account_p = [
    {"text": "🔥 {{username}}'s Account 🔥\n\n⚙️ My User Id: {{id}}\n🔎 My Total Lookups: {{total_lookups}}\n❤️ My First Visit: {{created_at}}\n💸 My Balance: {{balance}}$"}]
deposit_p = []
support_p = [
    {"text": "💬 Support Contacts 💬\n\nℹ️ You may reach us under the following tags:\n@StealthwayDeskSupport\n\nℹ️ Our Official Telegram Channel:\n@stealthwayshopfeedback"}]

commands = {"/start": start_p, "Start Lookup 🔎": start_lookup_p, "My Balance 💰": my_balance_p, "My Account ⚙️": my_account_p, "Deposit Balance 💵": deposit_p, "Support ℹ️": support_p}

