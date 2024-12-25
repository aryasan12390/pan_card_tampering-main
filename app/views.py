# Important imports
from app import app
from flask import request, render_template
import os
from skimage.metrics import structural_similarity
import imutils
import cv2
from PIL import Image
import pytesseract
import re

# Path to Tesseract executable (adjust for your system)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # Update if on Linux/Mac

# Adding path to config
app.config['INITIAL_FILE_UPLOADS'] = 'app/static/uploads'
app.config['EXISTNG_FILE'] = 'app/static/original'
app.config['GENERATED_FILE'] = 'app/static/generated'

# Route to home page
@app.route("/", methods=["GET", "POST"])
def index():
    # Execute if request is GET
    if request.method == "GET":
        return render_template("index.html")

    # Execute if request is POST
    if request.method == "POST":
        # Get uploaded image
        file_upload = request.files['file_upload']
        filename = file_upload.filename

        # Save and resize the uploaded image
        uploaded_image = Image.open(file_upload).resize((600, 400))  # Resize for better comparison
        uploaded_image_path = os.path.join(app.config['INITIAL_FILE_UPLOADS'], 'image.jpg')
        uploaded_image.save(uploaded_image_path)

        # Resize the original image to match dimensions
        original_image = Image.open(os.path.join(app.config['EXISTNG_FILE'], 'image.jpg')).resize((600, 400))
        original_image_path = os.path.join(app.config['EXISTNG_FILE'], 'image.jpg')
        original_image.save(original_image_path)

        # Read uploaded and original images as arrays
        original_array = cv2.imread(original_image_path)
        uploaded_array = cv2.imread(uploaded_image_path)

        # Convert images to grayscale
        original_gray = cv2.cvtColor(original_array, cv2.COLOR_BGR2GRAY)
        uploaded_gray = cv2.cvtColor(uploaded_array, cv2.COLOR_BGR2GRAY)

        # Calculate structural similarity
        (score, diff) = structural_similarity(original_gray, uploaded_gray, full=True)
        diff = (diff * 255).astype("uint8")

        # Calculate threshold and contours
        thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)

        # Draw contours on images
        for c in cnts:
            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(original_array, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv2.rectangle(uploaded_array, (x, y), (x + w, y + h), (0, 0, 255), 2)

        # Save output images
        cv2.imwrite(os.path.join(app.config['GENERATED_FILE'], 'image_original.jpg'), original_array)
        cv2.imwrite(os.path.join(app.config['GENERATED_FILE'], 'image_uploaded.jpg'), uploaded_array)
        cv2.imwrite(os.path.join(app.config['GENERATED_FILE'], 'image_diff.jpg'), diff)
        cv2.imwrite(os.path.join(app.config['GENERATED_FILE'], 'image_thresh.jpg'), thresh)

        # OCR: Extract text from the uploaded PAN card
        extracted_text = pytesseract.image_to_string(Image.open(uploaded_image_path))
        pan_number, name, dob = None, None, None

        # Process text to extract PAN-specific details
        for line in extracted_text.split('\n'):
            line = line.strip()
            if re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]$', line):  # Pattern for PAN number
                pan_number = line
            elif re.match(r'\d{2}/\d{2}/\d{4}', line):  # Pattern for DOB
                dob = line
            elif not pan_number and not dob and len(line) > 2:  # Potential name
                name = line

        # Render template with results
        return render_template(
            'index.html',
            pred=f"{round(score * 100, 2)}% Correct",
            pan_number=pan_number if pan_number else "Not Found",
            name=name if name else "Not Found",
            dob=dob if dob else "Not Found"
        )
