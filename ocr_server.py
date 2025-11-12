"""
OCR Server for reading text from images
"""
from flask import Flask, request, jsonify
import pytesseract
from PIL import Image
import tempfile
import os

app = Flask(__name__)

@app.route('/ocr', methods=['POST'])
def ocr():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    
    image_file = request.files['image']
    
    # Save the file to a temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
        image_file.save(temp_file.name)
        temp_path = temp_file.name

    try:
        # Open and process the image
        with Image.open(temp_path) as img:
            # Perform OCR using pytesseract
            text = pytesseract.image_to_string(img)
        
        # Clean up the temporary file
        os.unlink(temp_path)
        
        return jsonify({'text': text})
    except Exception as e:
        # Clean up the temporary file even if there's an error
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=9800)