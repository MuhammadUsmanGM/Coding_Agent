# OCR Server

## Overview
The OCR Server provides Optical Character Recognition capabilities to extract text from images. It uses pytesseract and PIL to process image files and extract readable text. It runs on port 9800.

## Key Features

### Image Format Support
- JPEG images
- PNG images
- GIF images
- Other formats supported by PIL
- Automatic format detection and processing

### Text Extraction
- Extracts text from image files using Tesseract OCR
- Handles various fonts and text styles
- Processes images asynchronously
- Returns extracted text in UTF-8 format

### Secure File Handling
- Temporarily stores uploaded images on the server
- Automatically cleans up temporary files after processing
- Validates file types and handles errors gracefully

## API Endpoints

### POST /ocr
Extract text from an uploaded image file.

**Request:**
- Form data with image file under the key `image`

**Response:**
```json
{
  "text": "Extracted text from the image..."
}
```

## Response Structure

### Success Response
- `text`: The extracted text from the image

### Error Response
- `error`: Description of the error that occurred

## Usage Examples

### Extracting Text from an Image
```python
import requests

# Upload an image file
with open('document.jpg', 'rb') as image_file:
    files = {'image': image_file}
    response = requests.post('http://localhost:9800/ocr', files=files)

result = response.json()
if 'text' in result:
    print("Extracted text:")
    print(result['text'])
elif 'error' in result:
    print(f"Error: {result['error']}")
```

### Processing Different Image Types
```python
import requests

# Process a PNG file
with open('screenshot.png', 'rb') as png_file:
    files = {'image': png_file}
    response = requests.post('http://localhost:9800/ocr', files=files)

result = response.json()
if 'text' in result:
    print("Text from screenshot:")
    print(result['text'])
```

## Implementation Notes

### Temporary File Management
The server creates temporary files for image processing and automatically removes them after OCR is complete. In case of errors, the server ensures temporary files are cleaned up.

### Asynchronous Processing
Uses asyncio to handle image processing operations, which can be CPU-intensive, without blocking the server.

### Error Handling
The server handles various potential errors during the OCR process, including:
- Invalid image formats
- Tesseract OCR errors
- File read/write issues
- Memory constraints during processing

## Security Considerations
- Only processes uploaded image files during the request
- Automatically cleans up temporary files after processing
- No permanent storage of uploaded images
- Validates file content (not just extension) before processing

## Error Handling
- 400: When no image file is provided in the request
- 500: For OCR processing errors or other server-side issues during text extraction