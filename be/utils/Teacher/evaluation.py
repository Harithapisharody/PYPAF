import ast
import importlib.util
import os
import glob
import copy
import csv
import multiprocessing
import dill
from difflib import SequenceMatcher
from Levenshtein import ratio

# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REFERENCE_FILE = os.path.join(BASE_DIR, "reference.py")
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")
OUTPUT_CSV = os.path.join(BASE_DIR, "evaluation_results.csv")
TIMEOUT = 0.5

def get_student_folder():
    if not os.path.exists(UPLOADS_DIR):
        print(f"Error: Uploads directory '{UPLOADS_DIR}' not found.")
        exit(1)
    subfolders = [f for f in os.listdir(UPLOADS_DIR) if os.path.isdir(os.path.join(UPLOADS_DIR, f))]
    if not subfolders:
        print(f"Error: No subfolders found in '{UPLOADS_DIR}'. Please upload student files.")
        exit(1)
    latest_folder = max(subfolders, key=lambda f: os.path.getmtime(os.path.join(UPLOADS_DIR, f)))
    return os.path.join(UPLOADS_DIR, latest_folder)

def read_file_content(file_path):
    try:
        with open(file_path, "r") as file:
            return file.read()
    except Exception as e:
        return f"Error reading {file_path}: {e}"

def load_module_safe(file_path, expected_functions):
    try:
        spec = importlib.util.spec_from_file_location("module", file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        missing_functions = [func for func in expected_functions if not hasattr(module, func)]
        if missing_functions:
            return None, f"Missing functions: {', '.join(missing_functions)}"
        return module, None
    except SyntaxError as e:
        return None, f"Syntax Error: {e}"
    except Exception as e:
        return None, f"Error: {e}"

def worker(conn, func, args):
    try:
        result = dill.loads(func)(*args)
        conn.send(result)
    except Exception as e:
        conn.send(f"Error: {e}")

def execute_with_timeout(func, args):
    parent_conn, child_conn = multiprocessing.Pipe()
    pickled_func = dill.dumps(func)
    process = multiprocessing.Process(target=worker, args=(child_conn, pickled_func, args))
    process.start()
    process.join(TIMEOUT)
    if process.is_alive():
        process.terminate()
        process.join()
        return "Timeout (Infinite Loop Detected)"
    return parent_conn.recv() if parent_conn.poll() else "Error: No Output"

class VariableNameReplacer(ast.NodeTransformer):
    def __init__(self):
        self.var_count = 0
        self.var_map = {}

    def visit_Name(self, node):
        if isinstance(node.ctx, (ast.Load, ast.Store, ast.Del)):
            if node.id not in self.var_map:
                self.var_count += 1
                self.var_map[node.id] = f"var_{self.var_count}"
            node.id = self.var_map[node.id]
        return node

def normalize_code(code):
    try:
        tree = ast.parse(code)
        transformer = VariableNameReplacer()
        transformed_tree = transformer.visit(tree)
        return ast.unparse(transformed_tree)
    except Exception:
        return code

def extract_operations(tree):
    operations = []
    return_statements = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func_name = getattr(node.func, "id", "unknown")
            operations.append(f"Call_{func_name}")
        elif isinstance(node, ast.Assign):
            if node.value and isinstance(node.value, ast.BinOp):
                op = type(node.value.op).__name__
                operations.append(f"Assign_{op}")
            elif node.value and isinstance(node.value, ast.Call):
                func_name = getattr(node.value.func, "id", "unknown")
                operations.append(f"Assign_Call_{func_name}")
            else:
                operations.append("Assign")
        elif isinstance(node, ast.If):
            operations.append("If")
        elif isinstance(node, ast.For):
            operations.append("For")
        elif isinstance(node, ast.While):
            operations.append("While")
        elif isinstance(node, ast.Return):
            return_statements += 1
        elif isinstance(node, ast.BinOp):
            op = type(node.op).__name__
            operations.append(f"Bin_{op}")
    if return_statements == 0:
        operations.append("NoReturn")
    return operations, return_statements > 0

def extract_function_names(tree):
    return [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]

def function_name_similarity(student_func, ref_func):
    lev_similarity = ratio(student_func, ref_func) * 100
    seq_similarity = SequenceMatcher(None, student_func, ref_func).ratio() * 100
    return (lev_similarity + seq_similarity) / 2

def extract_operations_fallback(code):
    operations = []
    return_statements = 0
    lines = code.splitlines()
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("def "):
            continue
        elif "return" in stripped:
            return_statements += 1
        elif stripped.startswith("if "):
            operations.append("If")
        elif stripped.startswith("for "):
            operations.append("For")
        elif stripped.startswith("while "):
            operations.append("While")
        elif "=" in stripped:
            if any(op in stripped for op in ["+", "-", "*", "/", "%"]):
                operations.append("Assign_BinOp")
            elif "(" in stripped and ")" in stripped:
                operations.append("Assign_Call")
            else:
                operations.append("Assign")
        elif any(op in stripped for op in ["+", "-", "*", "/", "%"]):
            operations.append("BinOp")
        elif "(" in stripped and ")" in stripped:
            operations.append("Call")
    if return_statements == 0:
        operations.append("NoReturn")
    return operations, return_statements > 0

def extract_function_names_fallback(code):
    functions = []
    for line in code.splitlines():
        stripped = line.strip()
        if stripped.startswith("def "):
            try:
                func_name = stripped.split("def ")[1].split("(")[0].strip()
                functions.append(func_name)
            except IndexError:
                continue
    return functions

def is_code_effectively_empty(code, expected_funcs):
    code = code.strip()
    if not code:
        return True
    funcs = extract_function_names_fallback(code)
    ops, has_return = extract_operations_fallback(code)
    has_expected_func = any(func in expected_funcs for func in funcs)
    has_meaningful_ops = any(op not in ["Assign", "NoReturn"] for op in ops) or has_return
    return not (has_expected_func or has_meaningful_ops)

def compare_algorithm_similarity(ref_code, student_code, expected_funcs):
    norm_ref_code = normalize_code(ref_code)
    norm_student_code = normalize_code(student_code)
    errors = []

    if is_code_effectively_empty(norm_student_code, expected_funcs):
        errors.append(f"No expected function found (expected: {', '.join(expected_funcs)})")
        ref_ops, ref_has_return = extract_operations_fallback(norm_ref_code)
        if ref_has_return:
            errors.append("Missing return statement")
        return 0.0, errors

    try:
        student_tree = ast.parse(norm_student_code)
        reference_tree = ast.parse(norm_ref_code)

        student_funcs = extract_function_names(student_tree)
        reference_funcs = extract_function_names(reference_tree)
        has_expected_func = any(func in expected_funcs for func in student_funcs)
        if not has_expected_func:
            errors.append(f"No expected function found (expected: {', '.join(expected_funcs)})")
        func_match = max(
            (function_name_similarity(st_func, ref_func) for st_func in student_funcs for ref_func in reference_funcs),
            default=0
        ) / 100

        student_ops, has_return = extract_operations(student_tree)
        reference_ops, ref_has_return = extract_operations(reference_tree)
        if ref_has_return and not has_return:
            errors.append("Missing return statement")
        matcher = SequenceMatcher(None, student_ops, reference_ops)
        op_similarity = matcher.ratio()

        ref_ops_set = set(reference_ops)
        student_ops_set = set(student_ops)
        op_overlap = len(ref_ops_set.intersection(student_ops_set)) / len(ref_ops_set) if ref_ops_set else 0

        structural_score = (op_similarity * 0.4) + (op_overlap * 0.6)
        loop_match = min(sum(1 for op in student_ops if "For" in op or "While" in op),
                         sum(1 for op in reference_ops if "For" in op or "While" in op))
        conditional_match = min(sum(1 for op in student_ops if "If" in op),
                                sum(1 for op in reference_ops if "If" in op))
        structural_score += (loop_match * 0.03) + (conditional_match * 0.03)
        structural_score = min(structural_score, 1)

        if "NoReturn" in student_ops:
            structural_score -= 0.15
        if op_overlap < 0.7:
            structural_score *= 0.3

        combined_score = (structural_score * 0.7) + (func_match * 0.3)
        if not has_expected_func and ref_has_return and not has_return:
            return 0.0, errors
        return min(max(combined_score, 0.1), 1), errors

    except (SyntaxError, IndentationError):
        student_funcs = extract_function_names_fallback(norm_student_code)
        reference_funcs = extract_function_names_fallback(norm_ref_code)
        has_expected_func = any(func in expected_funcs for func in student_funcs)
        if not has_expected_func:
            errors.append(f"No expected function found (expected: {', '.join(expected_funcs)})")
        func_match = max(
            (function_name_similarity(st_func, ref_func) for st_func in student_funcs for ref_func in reference_funcs),
            default=0
        ) / 100

        student_ops, has_return = extract_operations_fallback(norm_student_code)
        reference_ops, ref_has_return = extract_operations_fallback(norm_ref_code)
        if ref_has_return and not has_return:
            errors.append("Missing return statement")
        matcher = SequenceMatcher(None, student_ops, reference_ops)
        op_similarity = matcher.ratio()

        ref_ops_set = set(reference_ops)
        student_ops_set = set(student_ops)
        op_overlap = len(ref_ops_set.intersection(student_ops_set)) / len(ref_ops_set) if ref_ops_set else 0

        structural_score = (op_similarity * 0.4) + (op_overlap * 0.6)
        loop_match = min(sum(1 for op in student_ops if "For" in op or "While" in op),
                         sum(1 for op in reference_ops if "For" in op or "While" in op))
        conditional_match = min(sum(1 for op in student_ops if "If" in op),
                                sum(1 for op in reference_ops if "If" in op))
        structural_score += (loop_match * 0.03) + (conditional_match * 0.03)
        structural_score = min(structural_score, 1)

        if "NoReturn" in student_ops:
            structural_score -= 0.15
        if op_overlap < 0.7:
            structural_score *= 0.3

        combined_score = (structural_score * 0.7) + (func_match * 0.3)
        if not has_expected_func and ref_has_return and not has_return:
            return 0.0, errors
        return min(max(combined_score, 0.1), 1), errors

def extract_functions_and_tests(file_path):
    try:
        spec = importlib.util.spec_from_file_location("reference", file_path)
        reference_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(reference_module)
        test_cases = getattr(reference_module, "test_cases", [])
        func_names = [
            func for func in dir(reference_module)
            if callable(getattr(reference_module, func)) and not func.startswith("__")
        ]
        return func_names, test_cases, reference_module
    except Exception as e:
        return [], [], None

def assign_grade(similarity, passed_tests, total_tests, final_score, has_syntax_error=False, has_infinite_loop=False):
    # Normalize similarity and final_score (assuming input is in 0-100 scale)
    similarity /= 100
    final_score /= 100

    # Handle syntax errors or infinite loops
    if (has_syntax_error or has_infinite_loop) and passed_tests == 0:
        if similarity >= 0.7:
            return 'C'
        elif similarity >= 0.5:
            return 'D'
        elif similarity >= 0.4:
            return 'P'
        else:
            return 'F'

    # Case 1: All test cases passed
    if passed_tests == total_tests:
        return 'S' if similarity > 0.5 else 'D'

    # Case 2: No test cases passed
    if passed_tests == 0 or similarity < 0.5 or final_score < 0.4:
        return 'F'

    # Case 3: Half or more test cases passed - Assign grades based on final_score
    if passed_tests >= total_tests / 2:
        if final_score >= 0.9:
            return 'S'
        elif final_score >= 0.8:
            return 'A+'
        elif final_score >= 0.7:
            return 'A'
        elif final_score >= 0.6:
            return 'B+'
        elif final_score >= 0.5:
            return 'C+'
        elif final_score >= 0.4:
            return 'C'
        elif final_score >= 0.3:
            return 'P'
    
    # Case 4: Less than half test cases passed
    if similarity > 0.4:
        if final_score < 0.3:
            return 'P'
        if final_score < 0.5:
            return 'D'

    return 'F'


if __name__ == "__main__":
    STUDENT_FOLDER = get_student_folder()
    print(f"Using student folder: {STUDENT_FOLDER}")
    
    if not os.path.exists(REFERENCE_FILE):
        print(f"Error: Reference file '{REFERENCE_FILE}' not found.")
        exit(1)
    
    func_names, test_cases, reference_module = extract_functions_and_tests(REFERENCE_FILE)
    if not func_names:
        print(f"Error: No valid functions found in '{REFERENCE_FILE}'")
        exit(1)
    if not test_cases:
        print(f"Error: No test cases found in '{REFERENCE_FILE}'. Ensure 'test_cases' is defined.")
        exit(1)
    
    expected_outputs = {
        func_name: [execute_with_timeout(getattr(reference_module, func_name), copy.deepcopy(tc)) for tc in test_cases]
        for func_name in func_names
    }
    
    reference_code = read_file_content(REFERENCE_FILE)
    test_case_weights = [1.0 for _ in range(len(test_cases))]
    
    student_files = glob.glob(f"{STUDENT_FOLDER}/*.py")
    if not student_files:
        print(f"Warning: No student files found in '{STUDENT_FOLDER}'. Writing empty CSV.")
        with open(OUTPUT_CSV, mode='w', newline='') as csv_file:
            fieldnames = ["Student Name", "Algorithm Similarity (100)", "Test Case Passed", "Total Test Cases", "Final Score (100)", "Grade", "Error"]
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
        print(f"Evaluation complete (no files to evaluate). Results saved to {OUTPUT_CSV}")
        exit(0)
    
    with open(OUTPUT_CSV, mode='w', newline='') as csv_file:
        fieldnames = ["Student Name", "Algorithm Similarity (100)", "Test Case Passed", "Total Test Cases", "Final Score (100)", "Grade", "Error"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        
        for student_file in student_files:
            student_name = os.path.basename(student_file)
            print(f"\n[Evaluating] {student_name}...\n")

            student_code = read_file_content(student_file)
            student_module, error_message = load_module_safe(student_file, func_names)
            has_syntax_error = error_message and "Syntax Error" in error_message
            
            similarity_score, similarity_errors = compare_algorithm_similarity(reference_code, student_code, func_names)
            similarity_score_100 = similarity_score * 100  # Scale to 0–100
            print(f"[Similarity] Algorithm Similarity Score: {similarity_score_100:.2f}/100")
            print(f"{'[OK]' if similarity_score_100 >= 25 else '[Warning]'} {student_name} follows the expected algorithm structure.")
            if similarity_errors:
                for err in similarity_errors:
                    print(f"[Error] {err}")

            passed_test_cases = 0
            total_weighted_score = 0
            total_test_cases = len(test_cases)
            max_weighted_score = sum(test_case_weights)
            has_infinite_loop = False
            
            if not has_syntax_error and student_module:
                for i, test_input in enumerate(test_cases):
                    expected_output = expected_outputs[func_names[0]][i]
                    test_copy = copy.deepcopy(test_input)
                    try:
                        student_func = getattr(student_module, func_names[0])
                        student_output = execute_with_timeout(student_func, test_copy)
                    except Exception as e:
                        student_output = f"Error: {e}"
                    if student_output == "Timeout (Infinite Loop Detected)":
                        has_infinite_loop = True
                        break
                    is_correct = student_output == expected_output
                    test_case_score = test_case_weights[i] if is_correct else 0
                    passed_test_cases += int(is_correct)
                    total_weighted_score += test_case_score
                    print(f"Test {i+1}: {test_copy} -> {'[Correct]' if is_correct else f'[Incorrect] (Exp: {expected_output}, Out: {student_output})'} (Score: {test_case_score})")
            else:
                print("Skipping test cases due to syntax error or missing function.")

            total_test_score = (total_weighted_score / max_weighted_score) if max_weighted_score > 0 else 0
            # Scale final score to 100: 40% similarity, 60% test performance
            final_score_100 = (similarity_score * 40) + (total_test_score * 60)
            grade = assign_grade(similarity_score_100, passed_test_cases, total_test_cases, final_score_100, has_syntax_error, has_infinite_loop)
            print(f"\n[Final Score] {student_name}: {final_score_100:.2f}/100")
            print(f"[Test Cases] {passed_test_cases}/{total_test_cases}")
            print(f"[Grade] Assigned Grade: {grade}\n")

            error_msg = ""
            if has_infinite_loop:
                final_score_100 = similarity_score * 40  # Only similarity contributes if infinite loop
                grade = assign_grade(similarity_score_100, 0, total_test_cases, final_score_100, has_syntax_error, has_infinite_loop)
                error_msg = "Infinite Loop Detected"
                if similarity_errors:
                    error_msg += "; " + "; ".join(similarity_errors)
                writer.writerow({
                    "Student Name": student_name,
                    "Algorithm Similarity (100)": f"{similarity_score_100:.2f}",
                    "Test Case Passed": 0,
                    "Total Test Cases": total_test_cases,
                    "Final Score (100)": f"{final_score_100:.2f}",
                    "Grade": grade,
                    "Error": error_msg
                })
                continue
            
            if similarity_score_100 < 50:  # Adjusted threshold for 100-scale
                error_msg = "Algorithm does not follow expected structure"
            if error_message:
                error_msg = (error_msg + "; " if error_msg else "") + error_message
            if similarity_errors:
                error_msg = (error_msg + "; " if error_msg else "") + "; ".join(similarity_errors)

            writer.writerow({
                "Student Name": student_name,
                "Algorithm Similarity (100)": f"{similarity_score_100:.2f}",
                "Test Case Passed": passed_test_cases,
                "Total Test Cases": total_test_cases,
                "Final Score (100)": f"{final_score_100:.2f}",
                "Grade": grade,
                "Error": error_msg
            })
    
    print(f"Evaluation complete. Results saved to {OUTPUT_CSV}")