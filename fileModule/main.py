from flask import Flask, request, jsonify
import pytesseract
from PIL import Image
import io
import cv2
import numpy as np
import PyPDF2
from docx import Document
import textract
import os
from groq import Groq
import requests
import json
from dotenv import load_dotenv
from flask_socketio import SocketIO, emit

load_dotenv()

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize Groq client
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
server_url = os.environ.get("SERVER_URL")

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
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
    text = ""
    for page in pdf_reader.pages:
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

def verify_medical_document(text):
    prompt = f"""
    Analyze the following text and determine if it's a proper medical document. 
    If it is, extract and summarize the relevant medical details. 
    If it's not a medical document or doesn't contain relevant medical information, state that.

    Text to analyze:
    {text}

    Please provide your analysis in the following JSON format:
    {{
        "is_medical_document": true/false,
        "relevant_details": "Summarized relevant medical details if any, otherwise null",
        "explanation": "Brief explanation of your decision"
    }}
    """

    response = groq_client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        model="mixtral-8x7b-32768",
        temperature=0.1,
        max_tokens=1000,
        top_p=1,
        stream=False,
        stop=None
    )

    return response.choices[0].message.content

available_endpoints = """

Auth Routes (/auth):

POST /auth/signup

username: string (required)

email: string (required)

password: string (required)

fullName: string (optional)

role: 'doctor' | 'patient' | 'lab_technician' | 'admin' (optional, defaults to 'patient')

dateOfBirth: string (optional, date format)

phoneNumber: string (optional)

address: string (optional)

POST /auth/signin

email: string (required)

password: string (required)

GET /auth/me

(protected route, requires valid JWT token)

Patient Routes (/patient):

GET /patient/appointments

(protected route, requires valid JWT token)

GET /patient/diagnoses

(protected route, requires valid JWT token)

GET /patient/prescriptions

(protected route, requires valid JWT token)

PUT /patient/profile

(protected route, requires valid JWT token)

fullName: string (optional)

dateOfBirth: string (optional, date format)

phoneNumber: string (optional)

address: string (optional)

POST /patient/send-medication-reminder

(protected route, requires valid JWT token)

Admin Routes (/admin):

GET /admin/users

(protected route, requires valid JWT token and admin role)

GET /admin/users/:id

(protected route, requires valid JWT token and admin role)

id: number (required, user ID)

PUT /admin/users/:id

(protected route, requires valid JWT token and admin role)

id: number (required, user ID)

fullName: string (optional)

email: string (optional)

role: 'doctor' | 'patient' | 'lab_technician' | 'admin' (optional)

dateOfBirth: string (optional, date format)

phoneNumber: string (optional)

address: string (optional)

DELETE /admin/users/:id

(protected route, requires valid JWT token and admin role)

id: number (required, user ID)

GET /admin/appointments

(protected route, requires valid JWT token and admin role)

GET /admin/appointments/:id

(protected route, requires valid JWT token and admin role)

id: number (required, appointment ID)

PUT /admin/appointments/:id

(protected route, requires valid JWT token and admin role)

id: number (required, appointment ID)

userId: number (required)

doctorId: number (required)

dateTime: string (required, date & time format)

status: 'scheduled' | 'completed' | 'cancelled' (required)

DELETE /admin/appointments/:id

(protected route, requires valid JWT token and admin role)

id: number (required, appointment ID)

GET /admin/diagnoses

(protected route, requires valid JWT token and admin role)

GET /admin/diagnoses/:id

(protected route, requires valid JWT token and admin role)

id: number (required, diagnosis ID)

PUT /admin/diagnoses/:id

(protected route, requires valid JWT token and admin role)

id: number (required, diagnosis ID)

patientId: number (required)

doctorId: number (required)

diagnosis: string (required)

date: string (required, date format)

DELETE /admin/diagnoses/:id

(protected route, requires valid JWT token and admin role)

id: number (required, diagnosis ID)

GET /admin/prescriptions

(protected route, requires valid JWT token and admin role)

GET /admin/prescriptions/:id

(protected route, requires valid JWT token and admin role)

id: number (required, prescription ID)

PUT /admin/prescriptions/:id

(protected route, requires valid JWT token and admin role)

id: number (required, prescription ID)

patientId: number (required)

doctorId: number (required)

medication: string (required)

dosage: string (required)

frequency: string (required)

startDate: string (required, date format)

endDate: string (optional, date format)

DELETE /admin/prescriptions/:id

(protected route, requires valid JWT token and admin role)

id: number (required, prescription ID)

POST /admin/change-to-doctor/:id

(protected route, requires valid JWT token and admin role)

id: number (required, user ID)

specialization: string (required)

licenseNumber: string (required)

File Routes (/file):

POST /file/upload

(protected route, requires valid JWT token)

file: File (required, file to be uploaded)

Lab Routes (/lab):

POST /lab/tests

(protected route, requires valid JWT token)

patientId: number (required)

labId: number (required)

testName: string (required)

testDate: string (required, date format)

result: string (required)

referenceRange: string (optional)

interpretation: string (optional)

notes: string (optional)

GET /lab/tests

(protected route, requires valid JWT token)

GET /lab/tests/:id

(protected route, requires valid JWT token)

id: number (required, lab test ID)

PUT /lab/tests/:id

(protected route, requires valid JWT token)

id: number (required, lab test ID)

testName: string (optional)

testDate: string (optional, date format)

result: string (optional)

referenceRange: string (optional)

interpretation: string (optional)

notes: string (optional)

DELETE /lab/tests/:id

(protected route, requires valid JWT token)

id: number (required, lab test ID)

PUT /lab/profile

(protected route, requires valid JWT token)

fullName: string (optional)

dateOfBirth: string (optional, date format)

phoneNumber: string (optional)

address: string (optional)

Doctor Routes (/doctor):

GET /doctor/appointments

(protected route, requires valid JWT token)

GET /doctor/appointments/:id

(protected route, requires valid JWT token)

id: number (required, appointment ID)

PUT /doctor/appointments/:id

(protected route, requires valid JWT token)

id: number (required, appointment ID)

status: 'scheduled' | 'completed' | 'cancelled' (required)

POST /doctor/diagnoses

(protected route, requires valid JWT token)

patientId: number (required)

diagnosis: string (required)

date: string (required, date format)

GET /doctor/diagnoses/:patientId

(protected route, requires valid JWT token)

patientId: number (required)

POST /doctor/prescriptions

(protected route, requires valid JWT token)

patientId: number (required)

medication: string (required)

dosage: string (required)

frequency: string (required)

startDate: string (required, date format)

endDate: string (required, date format)

GET /doctor/prescriptions/:patientId

(protected route, requires valid JWT token)

patientId: number (required)

GET /doctor/profile

(protected route, requires valid JWT token)
"""

def process_natural_language(text, jwt_token):
    prompt = f"""
    Analyze the following natural language request and determine the appropriate API endpoint and parameters.
    If any necessary details are missing, identify them. Always assume that JWT and User ID is given.

    Request: {text}

    Available endpoints and their parameters:
    {available_endpoints}

    Respond in the following JSON format:
    {{
        "endpoint": "The appropriate endpoint path",
        "method": "GET/POST/PUT/DELETE",
        "parameters": {{
            "param1": "value1",
            "param2": "value2"
        }},
        "missing_details": ["detail1", "detail2", "detail3", ...] or null if no details are missing,
        "explanation": "Brief explanation of your decision"
    }}
    """

    response = groq_client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        model="mixtral-8x7b-32768",
        temperature=0.1,
        max_tokens=1000,
        top_p=1,
        stream=False,
        stop=None
    )

    return json.loads(response.choices[0].message.content)

def make_api_request(endpoint, method, parameters, jwt_token):
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }
    
    base_url = server_url  # Replace with your actual API base URL
    url = f"{base_url}{endpoint}"
    
    if method == "GET":
        response = requests.get(url, params=parameters, headers=headers)
    elif method == "POST":
        response = requests.post(url, json=parameters, headers=headers)
    elif method == "PUT":
        response = requests.put(url, json=parameters, headers=headers)
    elif method == "DELETE":
        response = requests.delete(url, json=parameters, headers=headers)
    else:
        return {"error": "Invalid HTTP method"}
    
    return response.json()

@app.route('/extract/', methods=['POST'])
def extract_text():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
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
        
        # Verify the extracted text using Groq
        verification_result = verify_medical_document(extracted_text)
        
        return jsonify({"result": verification_result})
    except Exception as e:
        return jsonify({"error": f"An error occurred during text extraction: {str(e)}"}), 500

@app.route('/process-request', methods=['POST'])
def process_request():
    data = request.json
    natural_language_request = data.get('request')
    jwt_token = request.headers.get('Authorization')
    
    if not natural_language_request:
        return jsonify({"error": "No request provided"}), 400
    
    if not jwt_token:
        return jsonify({"error": "No JWT token provided"}), 401
    
    processed_request = process_natural_language(natural_language_request, jwt_token)
    
    if processed_request.get('missing_details'):
        return jsonify({
            "error": "Missing details",
            "missing_details": processed_request['missing_details'],
            "explanation": processed_request['explanation']
        }), 400
    
    api_response = make_api_request(
        processed_request['endpoint'],
        processed_request['method'],
        processed_request['parameters'],
        jwt_token
    )
    
    return jsonify({
        "result": api_response,
        "explanation": processed_request['explanation']
    })

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('chat_message')
def handle_chat_message(message):
    prompt = f"""
    You are HelixAI, a healthcare assistant and nutritionist. Provide helpful and accurate information 
    based on the user's query. Remember to always advise the user to consult with 
    a healthcare professional or registered dietitian for personalized medical or nutritional advice.

    As a nutritionist, you can:
    1. Provide general information about healthy eating habits and balanced diets.
    2. Explain the nutritional value of different foods.
    3. Suggest meal ideas that align with general health guidelines.
    4. Discuss the importance of various nutrients and their sources.
    5. Offer general advice on weight management through nutrition.

    As a healthcare assistant, you can:
    1. Provide general health information and guidance.
    2. Explain common medical terms and procedures.
    3. Discuss general preventive health measures.
    4. Offer information about common health conditions.

    User query: {message}

    Respond in a friendly and informative manner, focusing on general health and nutrition information 
    and guidance. Do not provide specific medical diagnoses, treatment recommendations, or personalized diet plans.
    Always emphasize the importance of consulting with qualified professionals for personalized advice.
    """

    response = groq_client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        model="mixtral-8x7b-32768",
        temperature=0.7,
        max_tokens=500,
        top_p=1,
        stream=False,
        stop=None
    )

    ai_response = response.choices[0].message.content
    emit('ai_response', {'message': ai_response})

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=8000, debug=True)