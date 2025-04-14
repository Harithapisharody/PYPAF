from flask import Flask
from flask_cors import CORS
from routes import generate_pseudocode_route, run_code_route,teacher_code_route,evaluate_route# Correct import of the route
app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}})

# Register routes from routes.py
app.register_blueprint(generate_pseudocode_route)  # Register the blueprint correctly
app.register_blueprint(run_code_route)
app.register_blueprint(teacher_code_route)
app.register_blueprint(evaluate_route)


if __name__ == '__main__':
    app.run(debug=True)

