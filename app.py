import streamlit as st
import pytesseract
from PIL import Image
#import easyocr
import cv2
import numpy as np
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import os

# Initialize Google Drive Authentication
gauth = GoogleAuth()
gauth.LoadCredentialsFile("mycreds.txt")  # Load saved credentials if available

if gauth.credentials is None:
    gauth.LocalWebserverAuth()  # Authenticate manually
elif gauth.access_token_expired:
    gauth.Refresh()  # Refresh expired credentials
else:
    gauth.Authorize()  # Use existing credentials

gauth.SaveCredentialsFile("mycreds.txt")  # Save credentials

drive = GoogleDrive(gauth)

# Preprocess Image for OCR
def preprocess_image(image):
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
    return Image.fromarray(thresh)

# OCR Functions
def extract_text_tesseract(image):
    return pytesseract.image_to_string(image)

#reader = easyocr.Reader(["en"], gpu=False)
#def extract_text_easyocr(image):
    #return " ".join(reader.readtext(np.array(image), detail=0))

# Upload to Google Drive
# def upload_to_drive(text, ref_number):
#     file_path = f"{ref_number}.txt"
#     with open(file_path, "w", encoding="utf-8") as file:
#         file.write(text)
    
#     folder_id = '1SXT8l8R1i3LktVSxU5mosdU5TczIVT_F'  # Replace with your Google Drive Folder ID
#     file_drive = drive.CreateFile({'title': f"{ref_number}.txt", 'parents': [{'id': folder_id}]})
#     file_drive.SetContentFile(file_path)
#     file_drive.Upload()
    
#     os.remove(file_path)
#     return f"File {ref_number}.txt uploaded successfully"

# Upload to Google Drive
def upload_to_drive(text, ref_number):
    file_path = f"{ref_number}.txt"
    
    # Save text to a file
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(text)

    folder_id = '1SXT8l8R1i3LktVSxU5mosdU5TczIVT_F'  # Replace with your Google Drive Folder ID
    file_drive = drive.CreateFile({'title': f"{ref_number}.txt", 'parents': [{'id': folder_id}]})
    file_drive.SetContentFile(file_path)

    print(f"Uploading {file_path} to Google Drive...")
    file_drive.Upload()

    # Explicitly remove reference to file_drive before deleting
    file_drive = None  
    
    # Retry deleting file safely
    try:
        os.remove(file_path)
        print(f"File {file_path} deleted successfully")
    except PermissionError:
        print(f"Could not delete {file_path}, retrying...")
        import time
        time.sleep(2)  # Wait 2 seconds before retrying
        try:
            os.remove(file_path)
            print(f"File {file_path} deleted successfully after retry")
        except Exception as e:
            print(f"Final error deleting file {file_path}: {e}")

    return f"File {ref_number}.txt uploaded successfully"


# Streamlit UI
st.title("OCR Text Extraction Web App")

uploaded_file = st.file_uploader("Upload an Image (PNG, JPG, JPEG)", type=["png", "jpg", "jpeg"])

if uploaded_file:
    st.image(uploaded_file, caption="Uploaded Image")

    # OCR Method Selection
    ocr_method = st.selectbox("Select OCR Method", ["Tesseract"])

    # Perform OCR
    if st.button("Extract Text"):
        img = Image.open(uploaded_file)
        preprocessed_img = preprocess_image(img)

        extracted_text = extract_text_tesseract(preprocessed_img)  
        st.session_state["extracted_text"] = extracted_text
        st.text_area("Extracted Text", extracted_text, height=200)

# Save & Upload Text
if "extracted_text" in st.session_state:
    ref_number = st.text_input("Enter Reference Number")

    if ref_number and st.button("Save & Upload to Google Drive"):
        message = upload_to_drive(st.session_state["extracted_text"], ref_number)
        st.success(message)
