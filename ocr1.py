from flask import Flask, request, jsonify
import pytesseract
from PIL import Image
import io
import cv2
import numpy as np
import threading
import easyocr
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os

app = Flask(__name__)

# Initialize Google Drive Authentication
gauth = GoogleAuth()
gauth.LocalWebserverAuth()
drive = GoogleDrive(gauth)

# Image Preprocessing for Better OCR
def preprocess_image(image):
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
    return Image.fromarray(thresh)

# Tesseract OCR Extraction
def extract_text(image):
    return pytesseract.image_to_string(image)

# EasyOCR Extraction
reader = easyocr.Reader(["en"], gpu=False)
def extract_text_easyocr(image):
    return " ".join(reader.readtext(np.array(image), detail=0))

# API Endpoint for OCR (Tesseract)
@app.route("/ocr", methods=["POST"])
def ocr():
    if "image" not in request.files:
        return jsonify({"error": "Image is required"}), 400

    image = request.files["image"]
    img = Image.open(io.BytesIO(image.read()))
    preprocessed_img = preprocess_image(img)

    extracted_text = extract_text(preprocessed_img)

    return jsonify({"extracted_text": extracted_text})

# API Endpoint for OCR (EasyOCR)
@app.route("/easyocr", methods=["POST"])
def easyocr_api():
    if "image" not in request.files:
        return jsonify({"error": "Image is required"}), 400

    image = request.files["image"]
    img = Image.open(io.BytesIO(image.read()))
    preprocessed_img = preprocess_image(img)

    extracted_text = extract_text_easyocr(preprocessed_img)

    return jsonify({"extracted_text": extracted_text})

# API Endpoint to Save Extracted Text and Upload to Google Drive
@app.route("/save", methods=["POST"])
def save_text():
    data = request.json
    if "text" not in data or "ref_number" not in data:
        return jsonify({"error": "Text and reference number are required"}), 400
    
    ref_number = data["ref_number"]
    text = data["text"]
    
    file_path = f"{ref_number}.txt"
    print(f"File will be saved at: {file_path}")  # Debug log

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(text)

    upload_to_drive(file_path, ref_number)

    return jsonify({"message": "File saved and uploaded successfully", "filename": file_path})

# Google Drive Upload
# def upload_to_drive(file_path, ref_number):
#     try:
#         file_drive = drive.CreateFile({'title': f"{ref_number}.txt"})
#         file_drive.SetContentFile(file_path)
#         print(f"Uploading {file_path} to Google Drive...")
#         file_drive.Upload()
#         print(f"File uploaded successfully: {file_path}")

#       # Ensure file is deleted after upload
#         if os.path.exists(file_path):
#             print(f"Attempting to delete file: {file_path}")
#             os.remove(file_path)
#             print(f"File {file_path} deleted successfully")
#         else:
#             print(f"File {file_path} already deleted or not found")
#     except Exception as e:
#         print(f"Error uploading file: {e}")

# Google Drive Upload
def upload_to_drive(file_path, ref_number):
    try:
        folder_id = '1SXT8l8R1i3LktVSxU5mosdU5TczIVT_F'  # <-- Update this with your folder ID

        file_drive = drive.CreateFile({
            'title': f"{ref_number}.txt", 
            'parents': [{'id': folder_id}]  
        })
        file_drive.SetContentFile(file_path)
        print(f"Uploading {file_path} to Google Drive folder {folder_id}...")
        file_drive.Upload()
        print(f"File uploaded successfully: {file_path}")

        # Ensure file is deleted after upload
        if os.path.exists(file_path):
            print(f"Attempting to delete file: {file_path}")
            os.remove(file_path)
            print(f"File {file_path} deleted successfully")
        else:
            print(f"File {file_path} already deleted or not found")
    except Exception as e:
        print(f"Error uploading file: {e}")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
