
from controllers.api_provider import Telegram
chat_id = "5594467534"
keyboard = {
    'inline_keyboard': [
        [{'text': 'Button 1', 'callback_data': 'button1'}, {'text': 'Button 2', 'callback_data': 'button2'}],
        [{'text': 'Button 3', 'callback_data': 'button2'}],
        [{'text': 'Button 4', 'callback_data': 'button2'}, {'text': 'Button 5', 'callback_data': 'button2'}],

    ],
}




from controllers.api_provider import Telegram
chat_id = "5594467534"
keyboard = {
    'inline_keyboard': [
        [
            {"text": "🔎 MVR Lookup"},
            {"text": "🔎 SSN Lookup"},
            {"text": "🔎 SSN+DOB Lookup", "callback_data": "ssn_dob_lookup"}
        ],
        [
            {"text": "🔎 DL Lookup"},
            {"text": "🔎 DL2 Lookup"},
            {"text": "🔎 DOB Lookup"}
        ],
        [
            {"text": "🔎 DOB/VIN/DL/CAR/LICENSE PLATE Lookup"},
            {"text": "🔎 Professional License Lookup"},
        ],
        [
            {"text": "↙️ Other Lookups ↘️", "callback_data": "other_lookup"}
        ],
        [
            {"text": "🔎 Credit Score Lookup", "callback_data": "cs_lookup"}
        ],
        [
            {"text": "🔎 Business Lookup", "callback_data": "business_lookup"},
            {"text": "🔎 Phone Lookup", "callback_data": "business_lookup"}

        ],
        [
            {"text": "️⚡️ Reverse SSN"},
            {"text": "️⚡️ Reverse Phone"}
        ],
        [
            {"text":"⚡️ Reverse Address"},
            {"text": "⚡️ Reverse E-Mail"}
        ]
    ]
}




lookup_prices = {
    "🔎 MVR Lookup": 50,
    "🔎 SSN Lookup": 10,
    "🔎 SSN+DOB Lookup": 12,
    "🔎 DL Lookup": 10,
    "🔎 DL2 Lookup": 10,
    "🔎 DOB Lookup": 5,
    "🔎 DOB/VIN/DL/CAR/LICENSE PLATE Lookup": 15,
    "🔎 Professional License Lookup": 8,
    "🔎 Credit Score Lookup": 5,
    "🔎 Business Lookup": 8,
    "🔎 Phone Lookup": 8,
    "⚡️ Reverse SSN": 8,
    "⚡️ Reverse Phone": 8,
    "⚡️ Reverse Address": 8,
    "⚡️ Reverse E-Mail": 8
}

