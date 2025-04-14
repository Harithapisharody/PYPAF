# PyPAF: Python Program, Algorithm, and Flowchart Generator

**PyPAF** is an educational tool designed to help students convert natural language descriptions into structured algorithms, flowcharts, and executable Python code. It also assists teachers by automating code evaluation and feedback during lab exams.

---

## ✨ Features

- Convert natural language prompts into pseudocode.
- Transform pseudocode into structured algorithms and visual flowcharts.
- Automatically generate Python code using advanced AI models.
- Execute and test Python code in an integrated environment.
- Evaluate student code with test cases for accurate grading.
- User-friendly interface for smooth interaction.

---

## 🎯 Objective

- Simplify programming education by guiding students from idea to implementation.
- Automate code generation and evaluation to support instructors in lab settings.

---

## 🔧 Tech Stack

- **Frontend:** HTML, CSS, JavaScript  
- **Backend:** Python, Flask  
- **AI/ML Models:** Huggingface `SmolLM2-1.7B-Instruct`  
- **Flowchart Generation:** Graphviz  
- **API:** Blackbox.ai  
- **IDE:** Visual Studio Code

---

## 💻 System Requirements

### Software:
- Python 3.x
- Flask
- Graphviz
- VS Code or any preferred IDE

### Hardware:
- OS: Windows 10/11 64-bit
- CPU: Quad-core (Intel i5 / AMD Ryzen 5 or better)
- RAM: Minimum 8 GB (Recommended: 16 GB)
- GPU: Minimum 2 GB
- Storage: 256 GB SSD or more

---

## 🛠 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Harithapisharody/PYPAF.git
   cd PYPAF
   cd be


2. Create a virtual environment and activate it
    ```bash
    python -m venv env
    source env/bin/activate   # or `env\Scripts\activate` on Windows

3. Install dependencies:
    ```bash
    pip install -r requirements.txt

4. Run the Flask app:
    ```bash
    python app.py

5. Run Frontend separately
    cd ../fe  # Navigate to the frontend folder

---
## 📊 Project Architecture
- Algorithm & Flowchart Generator

- Code Generation Unit (Huggingface + Rule-based)

- Evaluation Engine (Student vs Reference Code)

- Frontend Interface


