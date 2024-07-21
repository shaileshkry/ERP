from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId

# Configure MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client['School']
teachers_collection = db['teachers']
students_collection = db['students']
classes_collection = db['classes']

# Create a blueprint
class_blueprint = Blueprint('class_blueprint', __name__)

def teacher_exists(username):
    return teachers_collection.find_one({"user_name": username}) is not None

def student_exists(username):
    return students_collection.find_one({"username": username}) is not None

def class_exists(class_code):
    return classes_collection.find_one({"class_code": class_code}) is not None

@class_blueprint.route('/add_class', methods=['POST'])
def add_class():
    try:
        class_data = request.json
        class_code = class_data['class_code']
        teacher_username = class_data['teacher_user_name']
        student_username = class_data['student_user_name']
        
        # Check if the class already exists in the classes collection
        if class_exists(class_code):
            return jsonify({"error": "Class already exists"}), 400

        # Check if the teacher exists in the teachers collection
        if not teacher_exists(teacher_username):
            return jsonify({"error": "Teacher not found"}), 404

        # Check if the student exists in the students collection
        if not student_exists(student_username):
            return jsonify({"error": "Student not found"}), 404

        classes_collection.insert_one(class_data)

        return jsonify({"message": "Class added successfully", "id": class_code}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@class_blueprint.route('/update_class/<class_code>', methods=['PUT'])
def update_class(class_code):
    try:
        class_data = request.json
        teacher_username = class_data.get('teacher_user_name', None)
        student_username = class_data.get('student_user_name', None)
        
        # Check if the class exists in the classes collection
        if not class_exists(class_code):
            return jsonify({"error": "Class not found"}), 404

        # Check if the teacher exists in the teachers collection
        if teacher_username and not teacher_exists(teacher_username):
            return jsonify({"error": "Teacher not found"}), 404

        # Check if the student exists in the students collection
        if student_username and not student_exists(student_username):
            return jsonify({"error": "Student not found"}), 404

        result = classes_collection.update_one({"class_code": class_code}, {"$set": class_data})

        if result.matched_count > 0:
            return jsonify({"message": "Class updated successfully"}), 200
        else:
            return jsonify({"error": "Class not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@class_blueprint.route('/delete_class/<class_code>', methods=['DELETE'])
def delete_class(class_code):
    try:
        # Check if the class exists in the classes collection
        if not class_exists(class_code):
            return jsonify({"error": "Class not found"}), 404

        result = classes_collection.delete_one({"class_code": class_code})

        if result.deleted_count > 0:
            return jsonify({"message": "Class deleted successfully"}), 200
        else:
            return jsonify({"error": "Class not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
