from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime

# Configure MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client['School']
teachers_collection = db['teachers']
staff_collection = db['staff']
teacher_salaries_collection = db['teacher_salaries']
staff_salaries_collection = db['staff_salaries']

# Create a blueprint
salary_blueprint = Blueprint('salary_blueprint', __name__)

def user_exists(username, user_type):
    if user_type == 'teacher':
        return teachers_collection.find_one({"user_name": username}) is not None
    elif user_type == 'staff':
        return staff_collection.find_one({"user_name": username}) is not None
    return False

def salary_exists(salary_id, user_type):
    if user_type == 'teacher':
        return teacher_salaries_collection.find_one({"_id": ObjectId(salary_id)}) is not None
    elif user_type == 'staff':
        return staff_salaries_collection.find_one({"_id": ObjectId(salary_id)}) is not None
    return False

def get_salaries_collection(user_type):
    if user_type == 'teacher':
        return teacher_salaries_collection
    elif user_type == 'staff':
        return staff_salaries_collection
    return None

@salary_blueprint.route('/add_salary', methods=['POST'])
def add_salary():
    try:
        salary_data = request.json
        user_username = salary_data['user_name']
        user_type = salary_data['user_type']

        # Check if the user exists in the respective collection
        if not user_exists(user_username, user_type):
            return jsonify({"error": f"{user_type.capitalize()} not found"}), 404

        salary_data['_id'] = ObjectId()
        salary_data['payment_date'] = datetime.strptime(salary_data['payment_date'], "%Y-%m-%d")

        collection = get_salaries_collection(user_type)
        if collection is not None:
            collection.insert_one(salary_data)
            return jsonify({"message": "Salary record added successfully", "id": str(salary_data['_id'])}), 201
        else:
            return jsonify({"error": "Invalid user type"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@salary_blueprint.route('/update_salary/<salary_id>', methods=['PUT'])
def update_salary(salary_id):
    try:
        salary_data = request.json
        user_username = salary_data.get('user_name', None)
        user_type = salary_data.get('user_type', None)

        # Check if the salary record exists in the respective salaries collection
        if not salary_exists(salary_id, user_type):
            return jsonify({"error": "Salary record not found"}), 404

        # Check if the user exists in the respective collection
        if user_username and user_type and not user_exists(user_username, user_type):
            return jsonify({"error": f"{user_type.capitalize()} not found"}), 404

        if 'payment_date' in salary_data:
            salary_data['payment_date'] = datetime.strptime(salary_data['payment_date'], "%Y-%m-%d")

        collection = get_salaries_collection(user_type)
        if collection is not None:
            result = collection.update_one({"_id": ObjectId(salary_id)}, {"$set": salary_data})
            if result.matched_count > 0:
                return jsonify({"message": "Salary record updated successfully"}), 200
            else:
                return jsonify({"error": "Salary record not found"}), 404
        else:
            return jsonify({"error": "Invalid user type"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@salary_blueprint.route('/delete_salary/<salary_id>', methods=['DELETE'])
def delete_salary(salary_id):
    try:
        user_type = request.args.get('user_type')
        
        # Check if the salary record exists in the respective salaries collection
        if not salary_exists(salary_id, user_type):
            return jsonify({"error": "Salary record not found"}), 404

        collection = get_salaries_collection(user_type)
        if collection is not None:
            result = collection.delete_one({"_id": ObjectId(salary_id)})
            if result.deleted_count > 0:
                return jsonify({"message": "Salary record deleted successfully"}), 200
            else:
                return jsonify({"error": "Salary record not found"}), 404
        else:
            return jsonify({"error": "Invalid user type"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500
