from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
from utils import user_exists  # Importing the user_exists function

# Configure MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client['School']  
users_collection = db['users']
students_collection = db['students']

# Create a blueprint
student_blueprint = Blueprint('student_blueprint', __name__)

@student_blueprint.route('/add_student', methods=['POST'])
def add_student():
    try:
        student_data = request.json
        username = student_data['username']
        
        print("*" * 15, flush=True)
        print('Username from request:', username, flush=True)

        # Check if the username exists in the users collection
        if not user_exists(username):
            all_users = list(users_collection.find({}))
            print('All users in collection:', all_users, flush=True)  # New debug statement
            return jsonify({"error": "Username does not exist"}), 400

        # Check if the student already exists in the students collection
        if students_collection.find_one({"username": username}):  # Change made here
            return jsonify({"error": "Student already exists"}), 400

        student_data['_id'] = ObjectId()
        student_data['username'] = username  # Use the username instead of user_id
        student_data['class'] = student_data['class']
        student_data['enrollment_date'] = student_data['enrollment_date']

        students_collection.insert_one(student_data)

        return jsonify({"message": "Student added successfully", "id": str(student_data['_id'])}), 201
    except Exception as e:
        print('Error occurred:', e, flush=True)
        return jsonify({"error": str(e)}), 500
