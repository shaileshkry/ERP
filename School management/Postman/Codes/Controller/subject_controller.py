from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId

# Configure MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client['School']
subjects_collection = db['subjects']

# Create a blueprint
subject_blueprint = Blueprint('subject_blueprint', __name__)

@subject_blueprint.route('/add_subject', methods=['POST'])
def add_subject():
    try:
        subject_data = request.json
        subject_code = subject_data['subject_code']
        
        # Check if the subject already exists in the subjects collection
        if subjects_collection.find_one({"subject_code": subject_code}):
            return jsonify({"error": "Subject already exists"}), 400

        subjects_collection.insert_one(subject_data)

        return jsonify({"message": "Subject added successfully", "id": subject_code}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@subject_blueprint.route('/update_subject/<subject_code>', methods=['PUT'])
def update_subject(subject_code):
    try:
        subject_data = request.json

        # Check if the subject exists in the subjects collection
        if not subjects_collection.find_one({"subject_code": subject_code}):
            return jsonify({"error": "Subject not found"}), 404

        result = subjects_collection.update_one({"subject_code": subject_code}, {"$set": subject_data})

        if result.matched_count > 0:
            return jsonify({"message": "Subject updated successfully"}), 200
        else:
            return jsonify({"error": "Subject not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@subject_blueprint.route('/delete_subject/<subject_code>', methods=['DELETE'])
def delete_subject(subject_code):
    try:
        result = subjects_collection.delete_one({"subject_code": subject_code})

        if result.deleted_count > 0:
            return jsonify({"message": "Subject deleted successfully"}), 200
        else:
            return jsonify({"error": "Subject not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
