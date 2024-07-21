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

def build_education_section(education_data):
    education_section = {}
    if '10th' in education_data:
        education_section['10th'] = education_data['10th']
    if '12th' in education_data:
        education_section['12th'] = education_data['12th']
    if 'graduation' in education_data:
        education_section['graduation'] = education_data['graduation']
    if 'post_graduation' in education_data:
        education_section['post_graduation'] = education_data['post_graduation']
    return education_section

def build_class_details(class_data):
    return {
        'current_class': class_data.get('current_class'),
        'section': class_data.get('section'),
        'roll_number': class_data.get('roll_number')
    }

def build_guardian_info(guardian_data):
    if guardian_data is None:
        return {}
    return {
        'name': guardian_data.get('name', ''),
        'relation': guardian_data.get('relation', ''),
        'contact': {
            'phone': guardian_data.get('contact', {}).get('phone', ''),
            'email': guardian_data.get('contact', {}).get('email', '')
        },
        'address': {
            'house_number': guardian_data.get('address', {}).get('house_number', ''),
            'town': guardian_data.get('address', {}).get('town', ''),
            'district': guardian_data.get('address', {}).get('district', ''),
            'state': guardian_data.get('address', {}).get('state', ''),
            'country': guardian_data.get('address', {}).get('country', ''),
            'pincode': guardian_data.get('address', {}).get('pincode', '')
        }
    }

@student_blueprint.route('/add_student', methods=['POST'])
def add_student():
    try:
        student_data = request.json
        username = student_data['username']
        
        # Debugging output
        print("*" * 15, flush=True)
        print('Username from request:', username, flush=True)

        # Check if the username exists in the users collection
        if not user_exists(username):
            all_users = list(users_collection.find({}))
            print('All users in collection:', all_users, flush=True)  # Debug statement
            return jsonify({"error": "Username does not exist"}), 400

        # Check if the student already exists in the students collection
        if students_collection.find_one({"username": username}):
            return jsonify({"error": "Student already exists"}), 400

        student_doc = {
            '_id': ObjectId(),
            'username': username,
            'class_details': build_class_details(student_data.get('class_details', {})),
            'enrollment_date': student_data.get('enrollment_date', ''),
            'education': build_education_section(student_data.get('education', {})),
            'guardian_info': build_guardian_info(student_data.get('guardian_info', {}))
        }

        students_collection.insert_one(student_doc)

        return jsonify({"message": "Student added successfully", "id": str(student_doc['_id'])}), 201
    except Exception as e:
        print('Error occurred:', e, flush=True)
        return jsonify({"error": str(e)}), 500

@student_blueprint.route('/get_student/<username>', methods=['GET'])
def get_student(username):
    try:
        student = students_collection.find_one({"username": username})
        
        if student:
            student['_id'] = str(student['_id'])  # Convert ObjectId to string for JSON serialization
            return jsonify(student), 200
        else:
            return jsonify({"error": "Student not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Add more routes to handle other student-specific operations if needed.
