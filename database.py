import os
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


# 🔌 CONNECT TO MONGODB (SAFE FOR RENDER)
# ✅ CREATE CLIENT ONLY ONCE
client = MongoClient(os.getenv("MONGO_URI"))

# ✅ DATABASE
db = client["vaani_ai"]

# 📦 COLLECTIONS
def get_users_collection():
    return db["users"]

def get_contact_collection():
    return db["contacts"]

def get_chat_collection():
    return db["chat_history"]


# 👤 REGISTER USER
def register_user(username, password):
    users = get_users_collection()

    # Check if user exists
    if users.find_one({"username": username}):
        return False

    hashed_password = generate_password_hash(password)

    users.insert_one({
        "username": username,
        "password": hashed_password
    })

    return True


# 🔐 LOGIN USER
def login_user(username, password):
    users = get_users_collection()

    user = users.find_one({"username": username})

    if user and check_password_hash(user["password"], password):
        return user

    return None


# 💬 SAVE CHAT
def save_chat(user_input, bot_response):
    chat = get_chat_collection()

    chat.insert_one({
        "user_input": user_input,
        "bot_response": bot_response,
        "timestamp": datetime.utcnow()
    })


# 📩 SAVE CONTACT MESSAGE
def save_contact(name, email, message):
    contacts = get_contact_collection()

    contacts.insert_one({
        "name": name,
        "email": email,
        "message": message,
        "timestamp": datetime.utcnow()
    })