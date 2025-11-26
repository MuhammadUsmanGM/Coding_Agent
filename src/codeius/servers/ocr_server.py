"""
OCR Server for reading text from images
"""
from flask import Flask, request, jsonify
import pytesseract
from PIL import Image
import tempfile
import os
import asyncio

app = Flask(__name__)

@app.route('/ocr', methods=['POST'])
async def ocr():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    
    image_file = request.files['image']
    
    # Save the file to a temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
        image_file.save(temp_file.name)
        temp_path = temp_file.name

    try:
        # Open and process the image asynchronously
        loop = asyncio.get_event_loop()
        img = await loop.run_in_executor(None, Image.open, temp_path)

        # Perform OCR using pytesseract
        text = await loop.run_in_executor(None, pytesseract.image_to_string, img)
        
        # Clean up the temporary file
        os.unlink(temp_path)
        
        return jsonify({'text': text})
    except Exception as e:
        # Clean up the temporary file even if there's an error
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9800)