from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime

# Configure MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client['School']
students_collection = db['students']
teachers_collection = db['teachers']
staff_collection = db['staff']
student_attendance_collection = db['student_attendance']
teacher_attendance_collection = db['teacher_attendance']
staff_attendance_collection = db['staff_attendance']

# Create a blueprint
attendance_blueprint = Blueprint('attendance_blueprint', __name__)

def user_exists(username, user_type):
    if user_type == 'student':
        return students_collection.find_one({"username": username}) is not None
    elif user_type == 'teacher':
        return teachers_collection.find_one({"user_name": username}) is not None
    elif user_type == 'staff':
        return staff_collection.find_one({"user_name": username}) is not None
    return False

def attendance_exists(attendance_id, user_type):
    if user_type == 'student':
        return student_attendance_collection.find_one({"_id": ObjectId(attendance_id)}) is not None
    elif user_type == 'teacher':
        return teacher_attendance_collection.find_one({"_id": ObjectId(attendance_id)}) is not None
    elif user_type == 'staff':
        return staff_attendance_collection.find_one({"_id": ObjectId(attendance_id)}) is not None
    return False

def get_attendance_collection(user_type):
    if user_type == 'student':
        return student_attendance_collection
    elif user_type == 'teacher':
        return teacher_attendance_collection
    elif user_type == 'staff':
        return staff_attendance_collection
    return None

@attendance_blueprint.route('/add_attendance', methods=['POST'])
def add_attendance():
    try:
        attendance_data = request.json
        user_username = attendance_data['user_name']
        user_type = attendance_data['user_type']

        # Check if the user exists in the respective collection
        if not user_exists(user_username, user_type):
            return jsonify({"error": f"{user_type.capitalize()} not found"}), 404

        attendance_data['_id'] = ObjectId()
        attendance_data['date'] = datetime.strptime(attendance_data['date'], "%Y-%m-%d")

        collection = get_attendance_collection(user_type)
        if collection is not None:
            collection.insert_one(attendance_data)
            return jsonify({"message": "Attendance record added successfully", "id": str(attendance_data['_id'])}), 201
        else:
            return jsonify({"error": "Invalid user type"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@attendance_blueprint.route('/update_attendance/<attendance_id>', methods=['PUT'])
def update_attendance(attendance_id):
    try:
        attendance_data = request.json
        user_username = attendance_data.get('user_name', None)
        user_type = attendance_data.get('user_type', None)

        # Check if the attendance record exists in the attendance collection
        if not attendance_exists(attendance_id, user_type):
            return jsonify({"error": "Attendance record not found"}), 404

        # Check if the user exists in the respective collection
        if user_username and user_type and not user_exists(user_username, user_type):
            return jsonify({"error": f"{user_type.capitalize()} not found"}), 404

        if 'date' in attendance_data:
            attendance_data['date'] = datetime.strptime(attendance_data['date'], "%Y-%m-%d")

        collection = get_attendance_collection(user_type)
        if collection is not None:
            result = collection.update_one({"_id": ObjectId(attendance_id)}, {"$set": attendance_data})
            if result.matched_count > 0:
                return jsonify({"message": "Attendance record updated successfully"}), 200
            else:
                return jsonify({"error": "Attendance record not found"}), 404
        else:
            return jsonify({"error": "Invalid user type"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@attendance_blueprint.route('/delete_attendance/<attendance_id>', methods=['DELETE'])
def delete_attendance(attendance_id):
    try:
        user_type = request.args.get('user_type')
        
        # Check if the attendance record exists in the attendance collection
        if not attendance_exists(attendance_id, user_type):
            return jsonify({"error": "Attendance record not found"}), 404

        collection = get_attendance_collection(user_type)
        if collection is not None:
            result = collection.delete_one({"_id": ObjectId(attendance_id)})
            if result.deleted_count > 0:
                return jsonify({"message": "Attendance record deleted successfully"}), 200
            else:
                return jsonify({"error": "Attendance record not found"}), 404
        else:
            return jsonify({"error": "Invalid user type"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500
