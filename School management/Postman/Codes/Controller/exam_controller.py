from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime

# Configure MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client['School']
classes_collection = db['classes']
subjects_collection = db['subjects']
exams_collection = db['exams']

# Create a blueprint
exam_blueprint = Blueprint('exam_blueprint', __name__)

def class_exists(class_code):
    return classes_collection.find_one({"class_code": class_code}) is not None

def subject_exists(subject_code):
    return subjects_collection.find_one({"subject_code": subject_code}) is not None

def exam_exists(exam_id):
    return exams_collection.find_one({"_id": ObjectId(exam_id)}) is not None

@exam_blueprint.route('/add_exam', methods=['POST'])
def add_exam():
    try:
        exam_data = request.json
        class_code = exam_data['class_code']
        subject_code = exam_data['subject_code']
        
        # Check if the class exists in the classes collection
        if not class_exists(class_code):
            return jsonify({"error": "Class not found"}), 404

        # Check if the subject exists in the subjects collection
        if not subject_exists(subject_code):
            return jsonify({"error": "Subject not found"}), 404

        exam_data['_id'] = ObjectId()
        exam_data['exam_date'] = datetime.strptime(exam_data['exam_date'], "%Y-%m-%d")

        exams_collection.insert_one(exam_data)

        return jsonify({"message": "Exam added successfully", "id": str(exam_data['_id'])}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@exam_blueprint.route('/update_exam/<exam_id>', methods=['PUT'])
def update_exam(exam_id):
    try:
        exam_data = request.json
        class_code = exam_data.get('class_code', None)
        subject_code = exam_data.get('subject_code', None)
        
        # Check if the exam exists in the exams collection
        if not exam_exists(exam_id):
            return jsonify({"error": "Exam not found"}), 404

        # Check if the class exists in the classes collection
        if class_code and not class_exists(class_code):
            return jsonify({"error": "Class not found"}), 404

        # Check if the subject exists in the subjects collection
        if subject_code and not subject_exists(subject_code):
            return jsonify({"error": "Subject not found"}), 404

        if 'exam_date' in exam_data:
            exam_data['exam_date'] = datetime.strptime(exam_data['exam_date'], "%Y-%m-%d")

        result = exams_collection.update_one({"_id": ObjectId(exam_id)}, {"$set": exam_data})

        if result.matched_count > 0:
            return jsonify({"message": "Exam updated successfully"}), 200
        else:
            return jsonify({"error": "Exam not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@exam_blueprint.route('/delete_exam/<exam_id>', methods=['DELETE'])
def delete_exam(exam_id):
    try:
        # Check if the exam exists in the exams collection
        if not exam_exists(exam_id):
            return jsonify({"error": "Exam not found"}), 404

        result = exams_collection.delete_one({"_id": ObjectId(exam_id)})

        if result.deleted_count > 0:
            return jsonify({"message": "Exam deleted successfully"}), 200
        else:
            return jsonify({"error": "Exam not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
