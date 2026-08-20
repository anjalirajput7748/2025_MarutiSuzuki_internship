#pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image
pytesseract.pytesseract.tesseract_cmd = r"C:\Users\566012\Desktop\Anjali_New folder\Tesseract-OCR\tesseract.exe"
POPPLER_PATH = r'C:\poppler-24.08.0\bin'
#"C:\poppler-24.08.0\bin"
from flask import Flask, request, jsonify
from flask_cors import CORS


app = Flask(__name__)
CORS(app)  # This allows frontend requests from different origins

@app.route('/', methods=['GET'])
def home():
    return jsonify({'message': 'Server is up and running!'})

#Add the OCR Endpoint:need to add a new route that accepts a PDF file and extracts text using OCR.
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image
@app.route('/extract-text', methods=['POST'])
def extract_text():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        images = convert_from_bytes(file.read(), poppler_path=POPPLER_PATH)
        extracted_text = ""

        for img in images:
            text = pytesseract.image_to_string(img)
            extracted_text += text + "\n"

        return jsonify({'extracted_text': extracted_text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)

