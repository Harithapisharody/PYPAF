from transformers import pipeline

def generate_code_from_logic(logic, pipe):
    """
    Generate Python code using the Hugging Face model.
    """
    try:
        # Define the prompt structure for Hugging Face model
        messages = [
            {"role": "system", "content": "You are an expe in generating python code. You must not include any other text other than the python code."},
            {"role": "user", "content": logic}
        ]

        # Generate code using Hugging Face model
        res = pipe(messages, max_new_tokens=1000)

        # Extract the generated Python code
        generated_code = res[0]['generated_text'][-1]['content'].replace('```python', '').replace('```', '')
        
        return generated_code
    except Exception as e:
        raise Exception(f"Error generating code: {e}")