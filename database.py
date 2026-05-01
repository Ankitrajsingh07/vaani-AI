from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
import os
# Connect to MongoDB
client = MongoClient(os.getenv("MONGO_URI"))
db = client["vaani_ai"]

# Collections
users_collection = db["users"]
chat_collection = db["chat_history"]
contact_collection = db["contacts"]



# USER FUNCTIONS


def register_user(username, password):
    hashed_password = generate_password_hash(password)

    user = {
        "username": username,
        "password": hashed_password
    }

    users_collection.insert_one(user)


def login_user(username, password):
    user = users_collection.find_one({"username": username})

    if user and check_password_hash(user["password"], password):
        return user
    return None



# CHAT FUNCTIONS


def save_chat(user_input, bot_response):
    chat = {
        "user_input": user_input,
        "bot_response": bot_response
    }

    chat_collection.insert_one(chat)



# CONTACT FORM


def save_contact(name, email, message):
    contact = {
        "name": name,
        "email": email,
        "message": message
    }

    contact_collection.insert_one(contact)