import streamlit as st
from PIL import Image
import pytesseract
from pathlib import Path
import random
from datetime import datetime

pytesseract.pytesseract.tesseract_cmd = r'/opt/homebrew/Cellar/tesseract/5.3.4_1/bin/tesseract'

st.set_page_config(
    page_title="Convert Image to Pdf",
    page_icon="👋",
)
st.title("Image to Pdf Utility")

def initLayout():
    FILE_TYPES = ["png","img","jpg"]
    uploaded_file = st.file_uploader("Choose image file for conversion", type=FILE_TYPES,accept_multiple_files=False)

    if uploaded_file is not None:
        img = Image.open(uploaded_file)
        fName = Path(uploaded_file.name).stem

        pdf = ocrFunction(img,"pdf")
        with open('test.pdf', 'w+b') as f:
            f.write(pdf) # pdf type is bytes by default
            #pdfByte = f.read()
            st.download_button(
                label="Click here to download pdf",
                data= pdf,
                file_name= fName+".pdf",
                mime="application/octet-stream"
                )
    
    img_file_buffer = st.camera_input("Take a picture to scan as pdf")
    if img_file_buffer :
        img = Image.open(img_file_buffer)
        pdf = ocrFunction(img,"pdf")
        pdfName = generateRandomFileName()
        with open('test.pdf', 'w+b') as f:
            f.write(pdf) # pdf type is bytes by default
            #pdfByte = f.read()
            st.download_button(
                label="Click here to download pdf",
                data= pdf,
                file_name= pdfName+".pdf",
                mime="application/octet-stream"
                )

def ocrFunction(img, ext):
        pdf = pytesseract.image_to_pdf_or_hocr(img, extension=ext)
        return pdf

def generateRandomFileName():
      return str(random.seed(datetime.now().timestamp()))


initLayout()