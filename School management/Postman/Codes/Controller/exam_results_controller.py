from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId

# Configure MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client['School']
students_collection = db['students']
exams_collection = db['exams']
exam_results_collection = db['exam_results']

# Create a blueprint
exam_results_blueprint = Blueprint('exam_results_blueprint', __name__)

def student_exists(username):
    return students_collection.find_one({"username": username}) is not None

def exam_exists(exam_id):
    return exams_collection.find_one({"_id": ObjectId(exam_id)}) is not None

def exam_result_exists(result_id):
    return exam_results_collection.find_one({"_id": ObjectId(result_id)}) is not None

@exam_results_blueprint.route('/add_exam_result', methods=['POST'])
def add_exam_result():
    try:
        result_data = request.json
        student_username = result_data['student']
        exam_id = result_data['exam']
        
        # Check if the student exists in the students collection
        if not student_exists(student_username):
            return jsonify({"error": "Student not found"}), 404

        # Check if the exam exists in the exams collection
        if not exam_exists(exam_id):
            return jsonify({"error": "Exam not found"}), 404

        result_data['_id'] = ObjectId()

        exam_results_collection.insert_one(result_data)

        return jsonify({"message": "Exam result added successfully", "id": str(result_data['_id'])}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@exam_results_blueprint.route('/update_exam_result/<result_id>', methods=['PUT'])
def update_exam_result(result_id):
    try:
        result_data = request.json
        student_username = result_data.get('student', None)
        exam_id = result_data.get('exam', None)
        
        # Check if the exam result exists in the exam results collection
        if not exam_result_exists(result_id):
            return jsonify({"error": "Exam result not found"}), 404

        # Check if the student exists in the students collection
        if student_username and not student_exists(student_username):
            return jsonify({"error": "Student not found"}), 404

        # Check if the exam exists in the exams collection
        if exam_id and not exam_exists(exam_id):
            return jsonify({"error": "Exam not found"}), 404

        result = exam_results_collection.update_one({"_id": ObjectId(result_id)}, {"$set": result_data})

        if result.matched_count > 0:
            return jsonify({"message": "Exam result updated successfully"}), 200
        else:
            return jsonify({"error": "Exam result not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@exam_results_blueprint.route('/delete_exam_result/<result_id>', methods=['DELETE'])
def delete_exam_result(result_id):
    try:
        # Check if the exam result exists in the exam results collection
        if not exam_result_exists(result_id):
            return jsonify({"error": "Exam result not found"}), 404

        result = exam_results_collection.delete_one({"_id": ObjectId(result_id)})

        if result.deleted_count > 0:
            return jsonify({"message": "Exam result deleted successfully"}), 200
        else:
            return jsonify({"error": "Exam result not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
