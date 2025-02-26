import streamlit as st
import requests

# Flask Backend URL
BACKEND_URL = "http://127.0.0.1:5000"  
st.title("📄 OCR Text Extraction Web App")

# Upload Image
uploaded_file = st.file_uploader("Upload an Image (PNG, JPG, JPEG)", type=["png", "jpg", "jpeg"])

if uploaded_file:
    st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)

    # OCR Method Selection
    ocr_method = st.selectbox("Select OCR Method", ["Tesseract", "EasyOCR"])

    # Perform OCR
    if st.button("Extract Text"):
        files = {"image": uploaded_file.getvalue()}
        endpoint = "/ocr" if ocr_method == "Tesseract" else "/easyocr"
        response = requests.post(f"{BACKEND_URL}{endpoint}", files=files)

        if response.status_code == 200:
            extracted_text = response.json()["extracted_text"]
            st.session_state["extracted_text"] = extracted_text  # Store extracted text
            st.text_area("Extracted Text", extracted_text, height=200)
        else:
            st.error("Error extracting text. Please try again.")

# Save & Upload Text
if "extracted_text" in st.session_state:
    ref_number = st.text_input("Enter Reference Number")

    if ref_number and st.button("Save & Upload to Google Drive"):
        save_data = {
            "text": st.session_state["extracted_text"],
            "ref_number": ref_number
        }
        response = requests.post(f"{BACKEND_URL}/save", json=save_data)

        if response.status_code == 200:
            st.success("Text saved and uploaded successfully!")
        else:
            st.error("Error saving text.")
