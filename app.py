from flask import Flask, render_template, request, jsonify
import os
from werkzeug.utils import secure_filename
import re
from pypdf import PdfReader
from utility_classes.gpt_manager import GPTManager
from utility_classes.tts_manager import TTSManager
from utility_classes.utility_functions import detect_language, translate
import base64

app = Flask(__name__)
gpt = GPTManager()
tts_manager = TTSManager()

# Config
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
        chat_history = data.get('chat_history', [])
        selected_language_code = data.get('language', 'en')  # Default to 'en' if not provided
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Map language codes to full names
        language_map = {'en': 'English', 'zh': 'Chinese'}
        selected_language_full = language_map.get(selected_language_code, 'English')

        # Get LLM output
        gpt_response = gpt.query(user_message, document_list, chat_history)
        print(f"GPT Response: {gpt_response}")

        # Detect language of GPT response
        detected_lang_full = detect_language(gpt_response)
        print(f"Detected Language: {detected_lang_full}")

        # Translate if necessary
        if detected_lang_full != selected_language_full:
            print(f"Translating from {detected_lang_full} to {selected_language_full}")
            gpt_response = translate(gpt_response, selected_language_full)
            print(f"Translated Response: {gpt_response}")

        # Generate audio
        audio_data = tts_manager.synthesize_speech(gpt_response)
        audio_base64 = base64.b64encode(audio_data).decode('utf-8') if audio_data else None

        return jsonify({
            'response': gpt_response,
            'audio': audio_base64,
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
                'message': f'File "{filename}" uploaded successfully ✅',
                'filename': filename,
                'status': 'success'
            })
        else:
            return jsonify({'error': 'File type not allowed'}), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
