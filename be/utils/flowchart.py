from graphviz import Digraph
import re

def generate_flowchart(pseudocode):
    steps = pseudocode.split("\n")
    flowchart = Digraph(format='png')
    flowchart.attr('node', shape='oval')

    flowchart.node('start', 'Start')
    prev_node = 'start'

    decision_stack = []
    loop_stack = []
    function_defs = {}
    else_edge_label = None
    inside_function = False
    current_function = None
    last_end_if_node = None  # Track last "End If" node

    # ✅ Fixed: Removed enumerate to correctly process each line
    for step in steps:
        step = step.strip()

        if not step or step.startswith("//") or step.lower().startswith("bag") or step.lower().startswith("begin") or step.lower().startswith("declare"):
            continue

        step_text = step.split(": ", 1)[-1].strip()

        if step.lower().startswith("Function"):
            func_match = re.match(r"Function\\s+(\\w+)\\s*\\((.*?)\\):", step)
            if func_match:
                func_name = func_match.group(1)
                inside_function = True
                current_function = func_name
                function_defs[func_name] = []
                flowchart.node(func_name, f"Function: {func_name}", shape='rectangle', style='filled', color='lightblue')
                continue

        if inside_function and (step.lower() == "end" or step.lower().startswith("def ")):
            inside_function = False
            current_function = None

        if inside_function and current_function:
            function_defs[current_function].append(step_text)
            continue

        call_match = re.match(r"(\\w+)\\((.*?)\\)", step_text)
        if call_match:
            called_func = call_match.group(1)
            if called_func in function_defs:
                node_id = f"call_{called_func}_{len(flowchart.body)}"
                flowchart.node(node_id, f"Call: {called_func}()", shape='box')
                flowchart.edge(prev_node, node_id)
                flowchart.edge(node_id, called_func, label="Executes")
                prev_node = node_id
                continue

        # Handle 'end' as Stop in oval
        if step_text.lower() == "end":
            flowchart.node('end', 'Stop', shape='oval')
            flowchart.edge(prev_node, 'end')
            break

        shape = 'box'
        node_id = f"step_{prev_node}_{len(flowchart.body)}"
        if step.lower().startswith("end if"):
            if decision_stack:
                last_decision = decision_stack.pop()
                last_end_if_node = last_decision  # Store last "End If" node
            continue 
        # node_id = f"step_{prev_node}_{len(flowchart.body)}"

        # Handle Output
        if "output" in step_text.lower():
            output_text = step_text.lower().replace("output", "", 1).strip()
            shape = 'parallelogram'
            node_id = f"display_{prev_node}_{len(flowchart.body)}"
            flowchart.node(node_id, f"Print: {output_text}", shape=shape)
            flowchart.edge(prev_node, node_id, label=else_edge_label if else_edge_label else "")
            prev_node = node_id
            else_edge_label = None

        # Handle Input
        elif "input" in step_text.lower():
            variable_name = step_text.split("input", 1)[-1].strip(": ").strip()
            shape = 'rectangle'
            node_id = f"input_{prev_node}_{len(flowchart.body)}"
            flowchart.node(node_id, f"{variable_name}", shape=shape)
            flowchart.edge(prev_node, node_id, label=else_edge_label if else_edge_label else "")
            prev_node = node_id
            else_edge_label = None
        


        elif "if" in step_text.lower() and "else if" not in step_text.lower():
            condition_match = re.search(r"if\s+(.*?)\s+then", step_text, re.IGNORECASE)
            condition_text = condition_match.group(1) if condition_match else "Condition"
            flowchart.node(node_id, f"If: {condition_text}", shape='diamond')
            flowchart.edge(prev_node, node_id)
            decision_stack.append(node_id)
            prev_node = node_id
            else_edge_label = "Yes"

        # Handle Else if
        elif "else if" in step_text.lower():
            if decision_stack:
                flowchart.edge(prev_node, 'end')
                last_decision = decision_stack[-1]
                node_id = f"elseif_{prev_node}_{len(flowchart.body)}"
                condition_match = re.search(r"else if\s+(.*?)\s+then", step_text, re.IGNORECASE)
                condition_text = condition_match.group(1)
                flowchart.node(node_id, f"Else If: {condition_text}", shape='diamond')
                flowchart.edge(last_decision, node_id, label="No")
                decision_stack[-1] = node_id
                prev_node = node_id
                else_edge_label = "Yes"

        # Handle Else
        elif "else" in step_text.lower():
            if decision_stack:
                flowchart.edge(prev_node, 'end')
                last_decision = decision_stack.pop()
                prev_node = last_decision
                else_edge_label = "No"

        

       # Handle End While first (to avoid collision)
        elif step.lower().startswith("end while"):
            print(f"End while detected for step: '{step_text}'")
            if loop_stack:
                while_node = loop_stack.pop()  # Get the corresponding while node
                flowchart.edge(prev_node, while_node, label="Back to Condition")  # Loop back
                prev_node = while_node


# Handle While loop after End While check
        elif step.lower().startswith("while"):
            condition_match = re.search(r"while\s+(.*?)\s+do", step_text, re.IGNORECASE)
            condition_text = condition_match.group(1) if condition_match else "While Condition"
            flowchart.node(node_id, f"While: {condition_text}", shape='diamond')
            flowchart.edge(prev_node, node_id)
            loop_stack.append(node_id)
            prev_node = node_id
            else_edge_label = "Yes"
            print("inside while")  # Debug print
            print(f"Step text received: '{step_text}'")


        elif step.lower().startswith("end for"):
            if loop_stack:
                for_node = loop_stack.pop()
                flowchart.edge(prev_node, for_node, label="Back to iteration")
                prev_node = for_node

        elif step.lower().startswith("for"):
            condition_match = re.search(r"for\s+(.*?)\s+from\s+(.*?)\s+to\s+(.*)", step_text, re.IGNORECASE)
            if condition_match:
                variable, start_val, end_val = condition_match.groups()
                condition_text = f"{variable} from {start_val} to {end_val}"
            else:
                condition_text = "For Condition"

            flowchart.node(node_id, f"For: {condition_text}", shape='diamond')
            flowchart.edge(prev_node, node_id, label=else_edge_label )  # ✅ Always print "Yes"
            loop_stack.append(node_id)
            prev_node = node_id
            else_edge_label = "Yes"  # ✅ Ensure Yes is labeled for each loop condition


     
        # Default case
        else:
            simplified_text = f"{step_text}"
            flowchart.node(node_id, simplified_text, shape=shape)
            flowchart.edge(prev_node, node_id, label=else_edge_label if else_edge_label else "")
            prev_node = node_id
            else_edge_label = None


    flowchart_filename = 'static/flowchart'
    flowchart.render(flowchart_filename, format='png')
    return flowchart_filename