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

def build_address_section(address_data):
    if address_data is None:
        return {}
    return {
        'house_number': address_data.get('house_number', ''),
        'town': address_data.get('town', ''),
        'district': address_data.get('district', ''),
        'state': address_data.get('state', ''),
        'country': address_data.get('country', ''),
        'pincode': address_data.get('pincode', '')
    }

def build_contact_details(contact_data):
    if contact_data is None:
        return {}
    emergency_contact = contact_data.get('emergency_contact', {})
    return {
        'email': contact_data.get('email', ''),
        'phone': contact_data.get('phone', ''),
        'emergency_contact': {
            'phone': emergency_contact.get('phone', ''),
            'email': emergency_contact.get('email', '')
        }
    }

def build_personal_info(personal_data):
    if personal_data is None:
        return {}
    return {
        'name': personal_data.get('name', ''),
        'date_of_birth': personal_data.get('date_of_birth', ''),
        'gender': personal_data.get('gender', ''),
        'contact_details': build_contact_details(personal_data.get('contact_details')),
        'category': personal_data.get('category', '')
    }

def build_name_occupation_details(info_data):
    if info_data is None:
        return {}
    return {
        'name': info_data.get('name', ''),
        'occupation': info_data.get('occupation', '')
    }

def build_parent_guardian_info(info_data):
    if info_data is None:
        return {}
    return {
        **build_name_occupation_details(info_data),
        'contact': build_contact_details(info_data.get('contact')),
        'address': build_address_section(info_data.get('address'))
    }

def build_parents_info(parents_data):
    if parents_data is None:
        return {}
    return {
        'fathers': build_parent_guardian_info(parents_data.get('fathers')),
        'mothers': build_parent_guardian_info(parents_data.get('mothers'))
    }

@user_blueprint.route('/add_user', methods=['POST'])
def add_user():
    try:
        user_data = request.json
        username = user_data.get('username')
        
        if user_exists(username):
            return jsonify({"error": "Username already exists"}), 400
        
        # Hash the password before storing it
        hashed_password = bcrypt.hashpw(user_data['password'].encode('utf-8'), bcrypt.gensalt())
        
        user_doc = {
            'username': username,
            'password': hashed_password,
            'role': user_data.get('role', ''),
            'personal_info': build_personal_info(user_data.get('personal_info')),
            'parents_info': build_parents_info(user_data.get('parents_info')),
            'address': {
                'permanent_address': build_address_section(user_data.get('address', {}).get('permanent_address')),
                'current_address': build_address_section(user_data.get('address', {}).get('current_address'))
            },
            'national_id': user_data.get('national_id', ''),
            'profile_picture_url': user_data.get('profile_picture_url', ''),
            'status': user_data.get('status', 'active'),
            'added_at': datetime.utcnow()
        }
        
        user_id = collection.insert_one(user_doc).inserted_id
        
        return jsonify({"message": "User added successfully", "user_id": str(user_id)}), 201
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
        username = user_data.get('username')
        password = user_data.get('password')
        
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
                    if field.startswith('personal_info') or field.startswith('parents_info') or field.startswith('address'):
                        update_data[field] = user_data[field]
                    else:
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
