from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime

# Configure MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client['School']
students_collection = db['students']
fees_collection = db['fees']

# Create a blueprint
fees_blueprint = Blueprint('fees_blueprint', __name__)

def student_exists(username):
    return students_collection.find_one({"username": username}) is not None

def fee_exists(fee_id):
    return fees_collection.find_one({"_id": ObjectId(fee_id)}) is not None

@fees_blueprint.route('/add_fee', methods=['POST'])
def add_fee():
    try:
        fee_data = request.json
        student_username = fee_data['student_username']
        
        # Check if the student exists in the students collection
        if not student_exists(student_username):
            return jsonify({"error": "Student not found"}), 404

        fee_data['_id'] = ObjectId()
        fee_data['due_date'] = datetime.strptime(fee_data['due_date'], "%Y-%m-%d")

        fees_collection.insert_one(fee_data)

        return jsonify({"message": "Fee record added successfully", "id": str(fee_data['_id'])}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@fees_blueprint.route('/update_fee/<fee_id>', methods=['PUT'])
def update_fee(fee_id):
    try:
        fee_data = request.json
        student_username = fee_data.get('student_username', None)
        
        # Check if the fee record exists in the fees collection
        if not fee_exists(fee_id):
            return jsonify({"error": "Fee record not found"}), 404

        # Check if the student exists in the students collection
        if student_username and not student_exists(student_username):
            return jsonify({"error": "Student not found"}), 404

        if 'due_date' in fee_data:
            fee_data['due_date'] = datetime.strptime(fee_data['due_date'], "%Y-%m-%d")

        result = fees_collection.update_one({"_id": ObjectId(fee_id)}, {"$set": fee_data})

        if result.matched_count > 0:
            return jsonify({"message": "Fee record updated successfully"}), 200
        else:
            return jsonify({"error": "Fee record not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@fees_blueprint.route('/delete_fee/<fee_id>', methods=['DELETE'])
def delete_fee(fee_id):
    try:
        # Check if the fee record exists in the fees collection
        if not fee_exists(fee_id):
            return jsonify({"error": "Fee record not found"}), 404

        result = fees_collection.delete_one({"_id": ObjectId(fee_id)})

        if result.deleted_count > 0:
            return jsonify({"message": "Fee record deleted successfully"}), 200
        else:
            return jsonify({"error": "Fee record not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
