from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId

# Configure MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client['School']
classes_collection = db['classes']
subjects_collection = db['subjects']
timetable_collection = db['timetable']

# Create a blueprint
timetable_blueprint = Blueprint('timetable_blueprint', __name__)

def class_exists(class_code):
    return classes_collection.find_one({"class_code": class_code}) is not None

def subject_exists(subject_code):
    return subjects_collection.find_one({"subject_code": subject_code}) is not None

def timetable_entry_exists(entry_id):
    return timetable_collection.find_one({"_id": ObjectId(entry_id)}) is not None

@timetable_blueprint.route('/add_timetable_entry', methods=['POST'])
def add_timetable_entry():
    try:
        entry_data = request.json
        class_code = entry_data['class_code']
        subject_code = entry_data['subject_code']
        
        # Check if the class exists in the classes collection
        if not class_exists(class_code):
            return jsonify({"error": "Class not found"}), 404

        # Check if the subject exists in the subjects collection
        if not subject_exists(subject_code):
            return jsonify({"error": "Subject not found"}), 404

        entry_data['_id'] = ObjectId()

        timetable_collection.insert_one(entry_data)

        return jsonify({"message": "Timetable entry added successfully", "id": str(entry_data['_id'])}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@timetable_blueprint.route('/update_timetable_entry/<entry_id>', methods=['PUT'])
def update_timetable_entry(entry_id):
    try:
        entry_data = request.json
        class_code = entry_data.get('class_code', None)
        subject_code = entry_data.get('subject_code', None)
        
        # Check if the timetable entry exists in the timetable collection
        if not timetable_entry_exists(entry_id):
            return jsonify({"error": "Timetable entry not found"}), 404

        # Check if the class exists in the classes collection
        if class_code and not class_exists(class_code):
            return jsonify({"error": "Class not found"}), 404

        # Check if the subject exists in the subjects collection
        if subject_code and not subject_exists(subject_code):
            return jsonify({"error": "Subject not found"}), 404

        result = timetable_collection.update_one({"_id": ObjectId(entry_id)}, {"$set": entry_data})

        if result.matched_count > 0:
            return jsonify({"message": "Timetable entry updated successfully"}), 200
        else:
            return jsonify({"error": "Timetable entry not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@timetable_blueprint.route('/delete_timetable_entry/<entry_id>', methods=['DELETE'])
def delete_timetable_entry(entry_id):
    try:
        # Check if the timetable entry exists in the timetable collection
        if not timetable_entry_exists(entry_id):
            return jsonify({"error": "Timetable entry not found"}), 404

        result = timetable_collection.delete_one({"_id": ObjectId(entry_id)})

        if result.deleted_count > 0:
            return jsonify({"message": "Timetable entry deleted successfully"}), 200
        else:
            return jsonify({"error": "Timetable entry not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
