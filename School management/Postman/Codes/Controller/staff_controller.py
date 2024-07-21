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
    return staff_collection.find_one({"username": username}) is not None

def build_experience_section(experience_data):
    return {
        'years_of_experience': experience_data.get('years_of_experience', 0),
        'previous_institutions': experience_data.get('previous_institutions', []),
        'areas_of_expertise': experience_data.get('areas_of_expertise', [])
    }

def build_qualifications_section(qualifications_data):
    return {
        'degrees': qualifications_data.get('degrees', []),
        'certifications': qualifications_data.get('certifications', []),
        'specializations': qualifications_data.get('specializations', [])
    }

def build_department_details(department_data):
    return {
        'department_name': department_data.get('department_name', ''),
        'position': department_data.get('position', '')
    }

@staff_blueprint.route('/add_staff', methods=['POST'])
def add_staff():
    try:
        staff_data = request.json
        username = staff_data['username']
        
        # Check if the username exists in the users collection
        if not user_exists(username):
            return jsonify({"error": "Username does not exist"}), 400
        
        # Check if the staff already exists in the staff collection
        if staff_exists(username):
            return jsonify({"error": "Staff member already exists"}), 400
        
        staff_doc = {
            '_id': ObjectId(),
            'username': username,
            'hire_date': datetime.strptime(staff_data['hire_date'], "%Y-%m-%d"),
            'experience': build_experience_section(staff_data.get('experience', {})),
            'qualifications': build_qualifications_section(staff_data.get('qualifications', {})),
            'department_details': build_department_details(staff_data.get('department_details', {})),
            'updated_at': datetime.utcnow()
        }

        staff_collection.insert_one(staff_doc)

        return jsonify({"message": "Staff member added successfully", "id": str(staff_doc['_id'])}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@staff_blueprint.route('/update_staff/<username>', methods=['PUT'])
def update_staff(username):
    try:
        staff_data = request.json
        
        # Check if the staff exists in the staff collection
        if not staff_exists(username):
            return jsonify({"error": "Staff member not found"}), 404
        
        update_doc = {
            'experience': build_experience_section(staff_data.get('experience', {})),
            'qualifications': build_qualifications_section(staff_data.get('qualifications', {})),
            'department_details': build_department_details(staff_data.get('department_details', {})),
            'updated_at': datetime.utcnow()
        }

        if 'hire_date' in staff_data:
            update_doc['hire_date'] = datetime.strptime(staff_data['hire_date'], "%Y-%m-%d")
        
        result = staff_collection.update_one({"username": username}, {"$set": update_doc})

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
        
        result = staff_collection.delete_one({"username": username})

        if result.deleted_count > 0:
            return jsonify({"message": "Staff member deleted successfully"}), 200
        else:
            return jsonify({"error": "Staff member not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
