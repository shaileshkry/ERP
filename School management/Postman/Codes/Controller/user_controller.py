from flask import Blueprint, request, jsonify
from utils import validate_user, user_exists  # Importing the functions from utils.py
from pymongo import MongoClient
import bcrypt
from datetime import datetime

# Configure MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client['School']
collection = db['users']

# Create a blueprint
user_blueprint = Blueprint('user_blueprint', __name__)

@user_blueprint.route('/add_user', methods=['POST'])
def add_user():
    try:
        user_data = request.json
        username = user_data.get('username')
        
        if user_exists(username):
            return jsonify({"error": "Username already exists"}), 400
        
        # Hash the password before storing it
        hashed_password = bcrypt.hashpw(user_data['password'].encode('utf-8'), bcrypt.gensalt())
        user_data['password'] = hashed_password
        
        # Add the current date and time
        user_data['added_at'] = datetime.utcnow()
        
        collection.insert_one(user_data)
        
        return jsonify({"message": "User added successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user_blueprint.route('/get_user/<username>', methods=['GET'])
def get_user(username):
    try:
        user = collection.find_one({"username": username})
        
        if user:
            user['_id'] = str(user['_id'])  # Convert ObjectId to string for JSON serialization
            user['password'] = user['password'].decode('utf-8')  # Decode bytes to string
            return jsonify(user), 200
        else:
            return jsonify({"error": "User not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user_blueprint.route('/login', methods=['POST'])
def login():
    try:
        login_data = request.json
        username = login_data['username']
        password = login_data['password']
        
        user = validate_user(username, password)
        
        if user:
            user['_id'] = str(user['_id'])  # Convert ObjectId to string for JSON serialization
            user['password'] = user['password'].decode('utf-8')  # Decode bytes to string
            
            return jsonify({"message": "Login successful", "user": user}), 200
        else:
            return jsonify({"error": "Invalid username or password"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user_blueprint.route('/update_user', methods=['PUT'])
def update_user():
    try:
        user_data = request.json
        username = user_data['username']
        password = user_data['password']
        
        user = validate_user(username, password)
        
        if user:
            update_data = {}
            
            # Hash the new password if it's being updated
            if 'new_password' in user_data:
                hashed_password = bcrypt.hashpw(user_data['new_password'].encode('utf-8'), bcrypt.gensalt())
                update_data['password'] = hashed_password
            
            # Add other fields to update data
            for field in user_data:
                if field not in ['username', 'password', 'new_password']:
                    update_data[field] = user_data[field]
            
            # Add the current date and time
            update_data['updated_at'] = datetime.utcnow()
            
            result = collection.update_one({"username": username}, {"$set": update_data})
            
            if result.matched_count > 0:
                return jsonify({"message": "User updated successfully"}), 200
            else:
                return jsonify({"error": "User not found"}), 404
        else:
            return jsonify({"error": "Invalid username or password"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user_blueprint.route('/delete_user', methods=['DELETE'])
def delete_user():
    try:
        user_data = request.json
        username = user_data['username']
        password = user_data['password']
        
        user = validate_user(username, password)
        
        if user:
            result = collection.delete_one({"username": username})
            
            if result.deleted_count > 0:
                return jsonify({"message": "User deleted successfully"}), 200
            else:
                return jsonify({"error": "User not found"}), 404
        else:
            return jsonify({"error": "Invalid username or password"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500
