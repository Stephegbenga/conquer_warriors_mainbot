from dotenv import load_dotenv
load_dotenv()
from pymongo import MongoClient
import os

environment=os.environ.get("environment")
db_name=os.environ.get("db_name")
DB_URL=os.environ.get('DB_URL')

conn = MongoClient(DB_URL)
db = conn.get_database(db_name)

# username, user_id, balance, created_at, total_lookups, variables, last_message, last_message_step
Users = db.get_collection("users")