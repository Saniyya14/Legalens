from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS  # ✅ Import Flask-CORS
from werkzeug.utils import secure_filename
import os

UPLOAD_FOLDER = 'uploads'
STANDARD_FOLDER = 'standards'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

app = Flask(__name__)
CORS(app)  # ✅ Enable CORS for all routes
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(STANDARD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_contract():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        lower_name = filename.lower()

        # Map keywords to folder names
        folder_map = {
            "freelance": "freelance_contract",
            "loan": "business_loan_contract",
            "rental": "rental_agreement_contract",
            "terms": "terms_and_conditions_contract"
        }

        # Determine target subfolder based on filename
        target_folder = None
        for keyword, folder in folder_map.items():
            if keyword in lower_name:
                target_folder = os.path.join(app.config['UPLOAD_FOLDER'], folder)
                break

        if not target_folder:
            return jsonify({'error': 'Filename does not match any known contract type'}), 400

        # Create subfolder if it doesn't exist
        os.makedirs(target_folder, exist_ok=True)

        filepath = os.path.join(target_folder, filename)
        file.save(filepath)

        return jsonify({
            'message': 'File uploaded successfully',
            'filename': filename,
            'folder': target_folder
        }), 200

    return jsonify({'error': 'Invalid file type'}), 400


@app.route('/standards', methods=['GET'])
def get_standard_files():
    files = os.listdir(STANDARD_FOLDER)
    return jsonify({'standards': files})

@app.route('/uploads/<filename>', methods=['GET'])
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
