from flask import Flask, render_template, request, jsonify
import os
from werkzeug.utils import secure_filename
from time import sleep
import re
from pypdf import PdfReader
from gpt import GPTManager
from test import markdown

app = Flask(__name__)
gpt = GPTManager()

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx', 'md'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
document_list = {}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        # gpt_response = markdown
        # Get LLM output
        gpt_response = gpt.query(user_message, document_list)
        print(gpt_response)

        return jsonify({
            'response': gpt_response,
            'status': 'success'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Read pdf and add it to document list
            reader = PdfReader(file_path)
            raw_pdf = " ".join([page.extract_text() for page in reader.pages])
            cleaned_pdf = re.sub(r'\n', ' ', raw_pdf)
            document_list[filename] = cleaned_pdf

            return jsonify({
                'message': f'File "{filename}" uploaded successfully',
                'filename': filename,
                'status': 'success'
            })
        else:
            return jsonify({'error': 'File type not allowed'}), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)