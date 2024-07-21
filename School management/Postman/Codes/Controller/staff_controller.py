from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
from utils import user_exists  # Importing the user_exists function
from datetime import datetime

# Configure MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client['School']
users_collection = db['users']
staff_collection = db['staff']

# Create a blueprint
staff_blueprint = Blueprint('staff_blueprint', __name__)

def staff_exists(username):
    return staff_collection.find_one({"user_name": username}) is not None

@staff_blueprint.route('/add_staff', methods=['POST'])
def add_staff():
    try:
        staff_data = request.json
        username = staff_data['user_name']
        
        # Check if the username exists in the users collection
        if not user_exists(username):
            return jsonify({"error": "Username does not exist"}), 400
        
        # Check if the staff already exists in the staff collection
        if staff_exists(username):
            return jsonify({"error": "Staff member already exists"}), 400
        
        staff_data['_id'] = ObjectId()
        staff_data['hire_date'] = datetime.strptime(staff_data['hire_date'], "%Y-%m-%d")
        staff_data['updated_at'] = datetime.utcnow()

        staff_collection.insert_one(staff_data)

        return jsonify({"message": "Staff member added successfully", "id": str(staff_data['_id'])}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@staff_blueprint.route('/update_staff/<username>', methods=['PUT'])
def update_staff(username):
    try:
        staff_data = request.json
        
        # Check if the staff exists in the staff collection
        if not staff_exists(username):
            return jsonify({"error": "Staff member not found"}), 404
        
        if 'hire_date' in staff_data:
            staff_data['hire_date'] = datetime.strptime(staff_data['hire_date'], "%Y-%m-%d")
        
        # Add the current date and time as updated_at
        staff_data['updated_at'] = datetime.utcnow()

        result = staff_collection.update_one({"user_name": username}, {"$set": staff_data})

        if result.matched_count > 0:
            return jsonify({"message": "Staff member updated successfully"}), 200
        else:
            return jsonify({"error": "Staff member not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@staff_blueprint.route('/delete_staff/<username>', methods=['DELETE'])
def delete_staff(username):
    try:
        # Check if the staff exists in the staff collection
        if not staff_exists(username):
            return jsonify({"error": "Staff member not found"}), 404
        
        result = staff_collection.delete_one({"user_name": username})

        if result.deleted_count > 0:
            return jsonify({"message": "Staff member deleted successfully"}), 200
        else:
            return jsonify({"error": "Staff member not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
