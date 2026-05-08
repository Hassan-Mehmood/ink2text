import base64
from io import BytesIO

import requests
import streamlit as st
from PIL import Image

API_URL = "http://localhost:8000/uploadfile/"

st.title("Ink2Text OCR")
st.write("Upload one or more images to extract text with bounding boxes.")

uploaded_files = st.file_uploader(
    "Choose images...", type=["jpg", "jpeg", "png"], accept_multiple_files=True
)

if uploaded_files:
    with st.spinner("Processing..."):
        files = [("files", (f.name, f.getvalue(), f.type)) for f in uploaded_files]
        try:
            response = requests.post(API_URL, files=files)
        except requests.ConnectionError:
            st.error(
                "Could not connect to the API. Make sure the FastAPI server is running on port 8000."
            )
            st.stop()

    if response.status_code == 200:
        result = response.json()
        annotated_images = result.get("images", [])
        all_data = result.get("data", [])

        st.subheader("Results")
        for idx, uploaded_file in enumerate(uploaded_files):
            st.divider()
            st.markdown(f"**Image {idx + 1}: {uploaded_file.name}**")

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("*Original*")
                st.image(uploaded_file, width="stretch")

            with col2:
                st.markdown("*Annotated*")
                if idx < len(annotated_images) and annotated_images[idx]:
                    img_bytes = base64.b64decode(annotated_images[idx])
                    annotated_image = Image.open(BytesIO(img_bytes))
                    st.image(annotated_image, width="stretch")
                else:
                    st.warning("No annotated image returned.")

            st.subheader("Detected Text")
            image_data = all_data[idx] if idx < len(all_data) else []
            if image_data:
                for item in image_data:
                    st.write(f"- {item.get('Text', '')}")
            else:
                st.write("No text detected.")

        st.subheader("Full JSON Response")
        st.json(result)
    else:
        st.error(f"Error {response.status_code}: {response.text}")
