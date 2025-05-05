import os
import json
from dotenv import load_dotenv
import requests
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import fitz  # PyMuPDF

# ---- Load environment variables from .env file ---- #
load_dotenv()
print("Loaded environment variables.")

# Manually set the environment variables (can be removed if already in .env)
os.environ["AZURE_OPENAI_API_KEY"] = "b177db0e754849a9a02239e6bb1d67f8"
os.environ["AZURE_OPENAI_ENDPOINT"] = "https://AzOpenAIBootcamp.openai.azure.com/"
DEPLOYMENT_NAME = "gpt-4o-mini"
API_VERSION = "2025-01-01-preview"

# ---- Fetch environment variables ---- #
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")

# ---- Ensure API credentials are loaded ---- #
if AZURE_OPENAI_KEY is None or AZURE_OPENAI_ENDPOINT is None:
    raise ValueError("Missing Azure OpenAI API Key or Endpoint in environment variables!")
else:
    print(f"AZURE_OPENAI_API_KEY: {AZURE_OPENAI_KEY}")
    print(f"AZURE_OPENAI_ENDPOINT: {AZURE_OPENAI_ENDPOINT}")

# ---- Flask setup ---- #
app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---- Helpers ---- #
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(filepath):
    text = ""
    with fitz.open(filepath) as doc:
        for page in doc:
            text += page.get_text()
    return text.strip()

def split_into_clauses(text):
    return [c.strip() for c in text.split('\n\n') if len(c.strip()) > 30]

def analyze_clause_with_gpt(clause):
    system_prompt = {
        "role": "system",
        "content": "You are a legal assistant that analyzes contract clauses."
    }

    user_prompt = {
        "role": "user",
        "content": f"""
Analyze the following clause from a contract.

Clause:
\"\"\"{clause}\"\"\"

Please:
1. Simplify the clause into plain English.
2. Assess whether this clause is standard or risky based on common legal practice.
3. Assign a risk flag: Green (standard), Yellow (some risk), or Orange (risky).
4. Provide a brief reason for the risk flag.

Return your response in this JSON format:
{{
  "simplified": "plain English version",
  "risk_flag": "Green | Yellow | Orange",
  "reason": "short reason"
}}
"""
    }

    headers = {
        'Content-Type': 'application/json',
        'api-key': AZURE_OPENAI_KEY
    }

    url = f"{AZURE_OPENAI_ENDPOINT}openai/deployments/{DEPLOYMENT_NAME}/chat/completions?api-version={API_VERSION}"

    data = {
        "messages": [system_prompt, user_prompt],
        "temperature": 0.3,
        "max_tokens": 400
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return {
            "simplified": "",
            "risk_flag": "Error",
            "reason": f"Request failed: {e}"
        }

    try:
        content = response.json()['choices'][0]['message']['content']
        return json.loads(content)
    except Exception as e:
        return {
            "simplified": "",
            "risk_flag": "Error",
            "reason": f"Failed to parse response: {e}"
        }

def calculate_risk_score(results):
    high_risk = sum(1 for r in results if r['risk_flag'] == 'Orange')
    medium_risk = sum(1 for r in results if r['risk_flag'] == 'Yellow')
    low_risk = sum(1 for r in results if r['risk_flag'] == 'Green')
    total = len(results)

    if total == 0:
        return {
            "high_risk_percentage": 0,
            "medium_risk_percentage": 0,
            "low_risk_percentage": 0,
            "exposure_score": 0
        }

    return {
        "high_risk_percentage": (high_risk / total) * 100,
        "medium_risk_percentage": (medium_risk / total) * 100,
        "low_risk_percentage": (low_risk / total) * 100,
        "exposure_score": (high_risk / total) * 100
    }

# ---- Route ---- #
@app.route('/compare-clauses', methods=['POST'])
def compare_clauses():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(path)

        user_text = extract_text_from_pdf(path)
        user_clauses = split_into_clauses(user_text)

        results = []
        for clause in user_clauses:
            analysis = analyze_clause_with_gpt(clause)
            analysis['original'] = clause
            results.append(analysis)

        risk_score = calculate_risk_score(results)

        return jsonify({
            'clauses': results,
            'risk_score': risk_score
        }), 200

    return jsonify({'error': 'Invalid file type'}), 400

# ---- Run ---- #
if __name__ == '__main__':
    app.run(debug=True)
