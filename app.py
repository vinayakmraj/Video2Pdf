from flask import Flask, request, redirect, url_for, send_file, render_template
import cv2
import time
from fpdf import FPDF
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'video' not in request.files:
        return 'No file part'
    file = request.files['video']
    if file.filename == '':
        return 'No selected file'
    if file:
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)
        pdf_path = process_video(filepath)
        return send_file(pdf_path, as_attachment=True)

def process_video(video_path):
    # Initialize the video capture
    cap = cv2.VideoCapture(video_path)
    
    # Define the time interval between frames (in seconds)
    frame_interval = 1  # Adjust this value to change the interval
    
    # Initialize variables
    frame_count = 0
    last_capture_time = time.time()
    screenshot_paths = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Check if it's time to capture a frame
        current_time = time.time()
        if current_time - last_capture_time >= frame_interval:
            # Save the frame as an image
            screenshot_path = f'frame_{frame_count:04d}.png'
            cv2.imwrite(screenshot_path, frame)
            screenshot_paths.append(screenshot_path)
            
            # Update variables
            frame_count += 1
            last_capture_time = current_time

    # Release the video capture
    cap.release()

    # Create a PDF and add screenshots to it
    pdf = FPDF()
    for screenshot_path in screenshot_paths:
        pdf.add_page()
        pdf.image(screenshot_path, x=10, y=10, w=190)
        os.remove(screenshot_path)  # Remove the screenshot after adding it to the PDF

    # Save the PDF
    pdf_output_path = os.path.join(UPLOAD_FOLDER, "screenshots.pdf")
    pdf.output(pdf_output_path)
    return pdf_output_path

if __name__ == '__main__':
    app.run(debug=True)
