from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
from utils import user_exists  # Importing the user_exists function
from datetime import datetime

# Configure MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client['School']
users_collection = db['users']
teachers_collection = db['teachers']
subjects_collection = db['subjects']

# Create a blueprint
teacher_blueprint = Blueprint('teacher_blueprint', __name__)

def subject_exists(subject_code):
    return subjects_collection.find_one({"subject_code": subject_code}) is not None

def teacher_exists(username):
    return teachers_collection.find_one({"username": username}) is not None

def build_experience_section(experience_data):
    return {
        'years_of_experience': experience_data.get('years_of_experience', ''),
        'previous_institutions': experience_data.get('previous_institutions', []),
        'areas_of_expertise': experience_data.get('areas_of_expertise', [])
    }

def build_qualifications_section(qualifications_data):
    return {
        'degrees': qualifications_data.get('degrees', []),
        'certifications': qualifications_data.get('certifications', []),
        'specializations': qualifications_data.get('specializations', [])
    }

@teacher_blueprint.route('/add_teacher', methods=['POST'])
def add_teacher():
    try:
        teacher_data = request.json
        username = teacher_data['username']
        subjects = teacher_data['subjects']
        
        # Check if the username exists in the users collection
        if not user_exists(username):
            return jsonify({"error": "Username does not exist"}), 400
        
        # Check if the teacher already exists in the teachers collection
        if teacher_exists(username):
            return jsonify({"error": "Teacher already exists"}), 400

        # Check if all subjects exist in the subjects collection
        for subject in subjects:
            if not subject_exists(subject):
                return jsonify({"error": f"Subject {subject} does not exist"}), 400
        
        teacher_doc = {
            '_id': ObjectId(),
            'username': username,
            'hire_date': datetime.strptime(teacher_data['hire_date'], "%Y-%m-%d"),
            'subjects': subjects,
            'experience': build_experience_section(teacher_data.get('experience', {})),
            'qualifications': build_qualifications_section(teacher_data.get('qualifications', {})),
            'updated_at': datetime.utcnow()
        }

        teachers_collection.insert_one(teacher_doc)

        return jsonify({"message": "Teacher added successfully", "id": str(teacher_doc['_id'])}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@teacher_blueprint.route('/update_teacher/<username>', methods=['PUT'])
def update_teacher(username):
    try:
        teacher_data = request.json
        subjects = teacher_data.get('subjects', [])
        
        # Check if the teacher exists in the teachers collection
        if not teacher_exists(username):
            return jsonify({"error": "Teacher not found"}), 404

        # Check if all subjects exist in the subjects collection
        for subject in subjects:
            if not subject_exists(subject):
                return jsonify({"error": f"Subject {subject} does not exist"}), 400

        update_doc = {
            'subjects': subjects,
            'experience': build_experience_section(teacher_data.get('experience', {})),
            'qualifications': build_qualifications_section(teacher_data.get('qualifications', {})),
            'updated_at': datetime.utcnow()
        }

        if 'hire_date' in teacher_data:
            update_doc['hire_date'] = datetime.strptime(teacher_data['hire_date'], "%Y-%m-%d")

        result = teachers_collection.update_one({"username": username}, {"$set": update_doc})

        if result.matched_count > 0:
            return jsonify({"message": "Teacher updated successfully"}), 200
        else:
            return jsonify({"error": "Teacher not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@teacher_blueprint.route('/delete_teacher/<username>', methods=['DELETE'])
def delete_teacher(username):
    try:
        # Check if the teacher exists in the teachers collection
        if not teacher_exists(username):
            return jsonify({"error": "Teacher not found"}), 404

        result = teachers_collection.delete_one({"username": username})

        if result.deleted_count > 0:
            return jsonify({"message": "Teacher deleted successfully"}), 200
        else:
            return jsonify({"error": "Teacher not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
