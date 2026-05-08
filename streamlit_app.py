import base64
from io import BytesIO

import requests
import streamlit as st
from PIL import Image

API_URL = "http://localhost:8000/uploadfile/"

st.title("Ink2Text OCR")
st.write("Upload an image to extract text with bounding boxes.")

uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Original Image")
        st.image(uploaded_file, width="stretch")

    with st.spinner("Processing..."):
        files = {
            "file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)
        }
        try:
            response = requests.post(API_URL, files=files)
        except requests.ConnectionError:
            st.error(
                "Could not connect to the API. Make sure the FastAPI server is running on port 8000."
            )
            st.stop()

    if response.status_code == 200:
        result = response.json()

        with col2:
            st.subheader("Annotated Image")
            img_base64 = result.get("image")
            if img_base64:
                img_bytes = base64.b64decode(img_base64)
                annotated_image = Image.open(BytesIO(img_bytes))
                st.image(annotated_image, width="stretch")
            else:
                st.warning("No annotated image returned.")

        st.subheader("Detected Text")
        data = result.get("data", [])
        if data:
            for item in data:
                st.write(f"- {item.get('Text', '')}")
        else:
            st.write("No text detected.")

        st.subheader("JSON Response")
        st.json(data)
    else:
        st.error(f"Error {response.status_code}: {response.text}")
