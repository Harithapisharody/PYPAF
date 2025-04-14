from flask import Blueprint, request, jsonify, send_file
from flask_cors import cross_origin
import os
import shutil
from utils.pseudocode import generate_pseudocode_from_logic
from utils.algorithm import generate_algorithm
from utils.flowchart import generate_flowchart
from utils.code_generation import generate_code_from_logic
import subprocess
from transformers import pipeline
import json
import time
import csv

# Define Blueprints
generate_pseudocode_route = Blueprint('generate_pseudocode', __name__)
teacher_code_route = Blueprint('generate_teacher_code', __name__)
run_code_route = Blueprint('run_code', __name__)
evaluate_route = Blueprint('evaluate', __name__)

# Pipeline for code generation (example usage)
pipe = pipeline("text-generation", model="HuggingFaceTB/SmolLM2-1.7B-Instruct", device=0)

# Function to replace folder contents with the new uploaded folder
def replace_folder(new_folder_path, target_folder_path):
    if os.path.exists(target_folder_path):
        shutil.rmtree(target_folder_path)

    os.makedirs(target_folder_path)

    for file_name in os.listdir(new_folder_path):
        full_file_name = os.path.join(new_folder_path, file_name)
        if os.path.isfile(full_file_name):
            shutil.copy(full_file_name, target_folder_path)

# Student pseudocode generation route
@generate_pseudocode_route.route('/generate/student', methods=['POST'])
@cross_origin()
def generate_student_pseudocode():
    try:
        data = request.get_json()
        logic = data.get('logic', '')

        if not logic:
            return jsonify({"status": "error", "text": "No logic provided!"}), 400

        pseudocode = generate_pseudocode_from_logic(logic)
        if not pseudocode:
            return jsonify({"status": "error", "text": "Failed to generate pseudocode!"}), 400

        algorithm = generate_algorithm(pseudocode)
        flowchart = generate_flowchart(pseudocode)
        code_generation = generate_code_from_logic(pseudocode, pipe)

        return jsonify({
            "pseudocode": pseudocode,
            "algorithm": algorithm,
            "flowchart": flowchart,
            "code_generation": code_generation,
        })

    except Exception as e:
        return jsonify({"status": "error", "text": str(e)}), 500

# Teacher pseudocode generation route
@teacher_code_route.route('/generate/teacher', methods=['POST'])
@cross_origin()
def generate_teacher_code():
    try:
        data = request.get_json()
        logic = data.get('logic', '')

        if not logic:
            return jsonify({"status": "error", "text": "No logic provided!"}), 400

        code_generation = generate_code_from_logic(logic, pipe)
        if not code_generation:
            return jsonify({"status": "error", "text": "Failed to generate code!"}), 400


        return jsonify({
            "code_generation": code_generation,
        })

    except Exception as e:
        return jsonify({"status": "error", "text": str(e)}), 500

# Save teacher code
@teacher_code_route.route('/save/generated_code', methods=['POST'])
@cross_origin()
def save_teacher_code():
    try:
        data = request.get_json()
        code = data.get('code', '')

        if not code:
            return jsonify({"status": "error", "text": "No code provided!"}), 400

        reference_file_path = os.path.join('utils', 'Teacher', 'reference.py')
        os.makedirs(os.path.dirname(reference_file_path), exist_ok=True)

        with open(reference_file_path, 'w') as file:
            file.write(code)

        return jsonify({
            "message": "Code successfully saved to utils/Teacher/reference.py"
        })

    except Exception as e:
        return jsonify({"status": "error", "text": f"Failed to save code: {str(e)}"}), 500

# Run code route
@run_code_route.route('/run', methods=['POST'])
@cross_origin()
def run_code():
    try:
        data = request.get_json()
        code = data.get('code', '')

        result = subprocess.run(
            ['python', '-c', code],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            return jsonify({"output": result.stdout})
        else:
            return jsonify({"error": result.stderr}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# New Route to handle folder uploads and replace old content
@teacher_code_route.route('/upload/folder', methods=['POST'])
@cross_origin()
def upload_folder():
    try:
        if 'folder' not in request.files:
            return jsonify({"status": "error", "text": "No folder uploaded!"}), 400

        uploaded_files = request.files.getlist('folder')

        if len(uploaded_files) == 0:
            return jsonify({"status": "error", "text": "No files in the folder!"}), 400

        target_folder_path = os.path.join(os.getcwd(), 'utils', 'Teacher', 'uploads')

        if os.path.exists(target_folder_path):
            try:
                shutil.rmtree(target_folder_path)
            except Exception as e:
                return jsonify({"status": "error", "text": f"Failed to delete old folder: {str(e)}"}), 500

        os.makedirs(target_folder_path, exist_ok=True)

        for file in uploaded_files:
            file_path = os.path.join(target_folder_path, file.filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            file.save(file_path)

        return jsonify({
            "message": "Folder uploaded and saved successfully"
        })

    except Exception as e:
        return jsonify({"status": "error", "text": f"Failed to upload folder: {str(e)}"}), 500

# Custom JSON encoder to handle NaN or None
class NanEncoder(json.JSONEncoder):
    def default(self, obj):
        if obj is None:
            return None
        return super().default(obj)

@evaluate_route.route('/evaluate', methods=['GET', 'POST'])
@cross_origin()
def evaluate_code():
    try:
        eval_script_path = os.path.join(os.getcwd(), 'utils', 'Teacher', 'evaluation.py')
        if not os.path.exists(eval_script_path):
            return jsonify({"status": "error", "text": f"Evaluation script not found at {eval_script_path}"}), 500

        result = subprocess.run(
            ['python', eval_script_path],
            capture_output=True,
            text=True,
            timeout=30
        )

        csv_path = os.path.join(os.getcwd(), 'utils', 'Teacher', 'evaluation_results.csv')
        csv_data = []
        if result.returncode == 0:
            time.sleep(3)
            if os.path.exists(csv_path):
                try:
                    with open(csv_path, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        csv_data = [row for row in reader]
                        for row in csv_data:
                            for key, value in row.items():
                                if value == '':
                                    row[key] = None
                except Exception as e:
                    csv_data = []
            else:
                csv_data = []

            response = {
                "status": "success",
                "message": "Evaluation completed successfully",
                "output": result.stdout,
                "csv_data": csv_data
            }
            return json.dumps(response, cls=NanEncoder), 200, {'Content-Type': 'application/json'}
        else:
            response = {
                "status": "error",
                "text": "Evaluation failed",
                "error": result.stderr,
                "stdout": result.stdout
            }
            return jsonify(response), 500

    except subprocess.TimeoutExpired as e:
        return jsonify({
            "status": "error",
            "text": "Evaluation timed out after 30 seconds",
            "error": e.stderr,
            "stdout": e.stdout
        }), 500
    except Exception as e:
        return jsonify({"status": "error", "text": f"Error running evaluation: {str(e)}"}), 500

@evaluate_route.route('/download_report', methods=['GET'])
@cross_origin()
def download_report():
    try:
        csv_path = os.path.join(os.getcwd(), 'utils', 'Teacher', 'evaluation_results.csv')
        
        if not os.path.exists(csv_path):
            return jsonify({"status": "error", "text": f"CSV file not found at {csv_path}"}), 404

        return send_file(csv_path, as_attachment=True, download_name="evaluation_results.csv")
    except Exception as e:
        return jsonify({"status": "error", "text": f"Error downloading report: {str(e)}"}), 500