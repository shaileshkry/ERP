from pymongo import MongoClient
import bcrypt

# Configure MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client['School']
collection = db['users']

def validate_user(username, password):
    user = collection.find_one({"username": username})
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
        return user
    return None

def user_exists(username):
    return collection.find_one({"username": username}) is not None
