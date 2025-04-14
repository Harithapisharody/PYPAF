import re

def generate_algorithm(translated_text):
    try:
        steps = ["Step 1: Start"]  # Start with the first step
        lines = translated_text.split('\n')  # Split text into lines
        step_no = 2  # Initialize step counter
        nested_stack = []  # Stack to track nested structures
        indent_levels = []  # Track indentation levels

        i = 0  # Variable to track the index in the lines
        while i < len(lines):
            line = lines[i]
            # Remove comments after "#" or "//"
            line = re.sub(r'(#|//).*', '', line).strip()
            
            if not line:  # Skip empty lines after removing comments
                i += 1
                continue
            
            stripped_line = line.lower().strip()  # Normalize the line
            indent = '    ' * len(nested_stack)  # Indentation based on nested stack size

            # Handle function definitions
            if stripped_line.startswith("function "):
                func_name = stripped_line.split('(')[0].replace('function ', '').strip()
                params = stripped_line.split('(')[1].split(')')[0]
                steps.append(f"Step {step_no}: Define the function '{func_name}' with inputs: {params}.")
                step_no += 1
                nested_stack.append("function")
                indent_levels.append(indent)

            # Handle variable assignment
            elif "=" in stripped_line and not stripped_line.startswith(("if", "elif", "else", "return", "print")) and "==" not in stripped_line:
                var, value = map(str.strip, stripped_line.split('=', 1))
                steps.append(f"{indent}Step {step_no}: Assign value '{value}' to the variable '{var}'.")
                step_no += 1

            # Handle return statements
            elif stripped_line.startswith("return"):
                return_value = stripped_line.replace("return", "").strip()
                steps.append(f"{indent}Step {step_no}: Return the value '{return_value}'.")
                step_no += 1

            # Handle conditional statements (if, elif, else)
            elif stripped_line.startswith("if"):
                condition = stripped_line[3:].strip().rstrip("then").strip()
                steps.append(f"{indent}Step {step_no}: Check if the condition '{condition}' is true.")
                step_no += 1
                nested_stack.append("if")
                indent_levels.append(indent)

            elif stripped_line.startswith("elif") or stripped_line.startswith("else if"):
                condition = stripped_line.split("if")[-1].strip().rstrip("then").strip()
                steps.append(f"{indent}Step {step_no}: Else If, check '{condition}'.")
                step_no += 1

            elif stripped_line.startswith("else"):
                steps.append(f"{indent}Step {step_no}:Execute the else block, If all previous conditions are false")
                step_no += 1

            # Handle output statements and subsequent input handling
            elif "output" in stripped_line:
                output_value = stripped_line.replace("output", "").strip().strip('"')
                
                # Check if next line contains an 'input' statement
                if i + 1 < len(lines) and "input" in lines[i + 1].lower():
                    next_line = lines[i + 1].lower().strip()
                    if "input" in next_line:
                        variable_name = next_line.replace("input", "").strip()
                        steps.append(f"{indent}Step {step_no}: Display the message '{output_value}' and store to the variable '{variable_name}'.")
                        step_no += 1
                    i += 1  # Skip the next input line as it is already processed
                else:
                    steps.append(f"{indent}Step {step_no}: Display the message '{output_value}'.")
                    step_no += 1

            # Handle 'for' loops
            elif stripped_line.startswith("for"):
                loop_content = stripped_line[4:].strip().rstrip(":")
                steps.append(f"{indent}Step {step_no}: Iterate a for loop {loop_content}.")
                step_no += 1
                nested_stack.append("for")
                indent_levels.append(indent)

            # Handle 'while' loops
            elif stripped_line.startswith("while"):
                condition = stripped_line[5:].strip().rstrip(":")
                steps.append(f"{indent}Step {step_no}: While the condition '{condition}' is true, repeat the following steps.")
                step_no += 1
                nested_stack.append("while")
                indent_levels.append(indent)

            # Handle block endings
            elif stripped_line.startswith("end "):
                if nested_stack:
                    nested_stack.pop()
                    indent_levels.pop()

            # Additional dynamic cases (you can add more as per requirements)
            elif "declare" in stripped_line:
                var_declaration = stripped_line.replace("declare", "").strip()
                steps.append(f"{indent}Step {step_no}: Declare the variable '{var_declaration}'.")
                step_no += 1

            i += 1  # Increment line index to continue processing the next line

        # Finalize the algorithm with a stop step
        steps.append(f"Step {step_no}: Stop")
        return "\n".join(steps)

    except Exception as e:
        return f"Error: {str(e)}"
