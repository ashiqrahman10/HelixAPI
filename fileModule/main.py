from flask import Flask, request, jsonify
import pytesseract
from PIL import Image
import io
import cv2
import numpy as np
import PyPDF2
from docx import Document
import textract

app = Flask(__name__)

def preprocess_image(image):
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply thresholding to preprocess the image
    gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    
    # Apply dilation to remove noise
    kernel = np.ones((1, 1), np.uint8)
    gray = cv2.dilate(gray, kernel, iterations=1)
    
    return gray

def perform_ocr(image):
    # Preprocess the image
    preprocessed = preprocess_image(image)
    
    # Perform OCR on the preprocessed image
    text = pytesseract.image_to_string(preprocessed)
    
    return text

def extract_text_from_pdf(file_content):
    # Log the file content
    print(file_content)
    print("Extracting text from PDF")
    
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
    text = ""
    for page in pdf_reader.pages:
        print(page.extract_text())
        text += page.extract_text()
    return text

def extract_text_from_doc(file_content):
    doc = Document(io.BytesIO(file_content))
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

def extract_text_from_other(file_content, file_extension):
    try:
        text = textract.process(io.BytesIO(file_content), extension=file_extension).decode('utf-8')
        return text
    except:
        return None

@app.route('/extract/', methods=['POST'])
def extract_text():
    print(request.files)
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    print(file.filename)
    content_type = file.content_type
    file_extension = file.filename.split('.')[-1].lower()

    try:
        contents = file.read()
        
        if content_type.startswith('image/'):
            nparr = np.frombuffer(contents, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            extracted_text = perform_ocr(image)
        elif file_extension == 'pdf':
            extracted_text = extract_text_from_pdf(contents)
        elif file_extension in ['doc', 'docx']:
            extracted_text = extract_text_from_doc(contents)
        else:
            extracted_text = extract_text_from_other(contents, file_extension)
        
        if extracted_text is None:
            return jsonify({"error": "Unsupported file format"}), 400
        
        return jsonify({"extracted_text": extracted_text})
    except Exception as e:
        return jsonify({"error": f"An error occurred during text extraction: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)