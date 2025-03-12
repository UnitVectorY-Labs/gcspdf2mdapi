import sys
import os
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
import io
import tempfile
from flask import Flask, request, jsonify
from google.cloud import storage
import pymupdf4llm

app = Flask(__name__)

def download_from_gcs(gcs_path, local_path):
    """
    Download file from GCS to a local path.
    Format of gcs_path should be: gs://bucket-name/path/to/file.pdf
    """
    try:
        if not gcs_path.startswith('gs://'):
            raise ValueError("GCS path must start with gs://")
        
        path_without_prefix = gcs_path[5:]  # remove 'gs://'
        bucket_name = path_without_prefix.split('/')[0]
        blob_path = '/'.join(path_without_prefix.split('/')[1:])
        
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_path)
        
        blob.download_to_filename(local_path)
        print(f"Successfully downloaded file to {local_path}")
        return True
    except Exception as e:
        print(f"Error downloading from GCS: {str(e)}")
        return False

def pdf_direct_to_markdown(pdf_path):
    """Convert PDF to markdown text"""
    try:
        # Open the PDF
        doc = fitz.open(pdf_path)
        
        # Use pymupdf4llm to convert to markdown
        markdown_text = pymupdf4llm.to_markdown(doc)
        
        return markdown_text, None
    except Exception as e:
        return None, str(e)

def pdf_to_markdown(pdf_path):
    """Convert PDF to markdown text using OCR per page."""
    try:
        doc = fitz.open(pdf_path)
        full_text = ""
        zoom = 1.2
        mat = fitz.Matrix(zoom, zoom)
        for page in doc:
            # Render page as image with zoom for better OCR accuracy
            pix = page.get_pixmap(matrix=mat)
            # Convert pixmap to in-memory JPEG
            img_bytes = pix.tobytes("jpeg")
            image = Image.open(io.BytesIO(img_bytes))
            # Perform OCR on the image using pytesseract
            res = pytesseract.image_to_string(image)
            full_text += res + "\n"
        # For this example, we return the raw OCR text.
        # You can further process the text to add Markdown formatting if needed.
        markdown_text = full_text
        return markdown_text, None
    except Exception as e:
        return None, str(e)

@app.route('/convert', methods=['POST'])
def convert_pdf():
    request_data = request.get_json()
    if not request_data or 'file' not in request_data:
        return jsonify({'error': 'Missing "file" parameter in request'}), 400
    
    gcs_path = request_data['file']
    
    # Get the mode parameter with a default value of "ocr"
    mode = request_data.get('mode', 'ocr')
    
    # Validate mode parameter
    if mode not in ['ocr', 'direct']:
        return jsonify({'error': 'Invalid mode parameter. Must be "ocr" or "direct"'}), 400
    
    # Create a temporary file to store the downloaded PDF
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
        temp_path = temp_file.name
    
    try:
        # Download file from GCS
        if not download_from_gcs(gcs_path, temp_path):
            return jsonify({'error': 'Failed to download file from GCS'}), 400
        
        # Convert the PDF to markdown using the specified mode
        if mode == 'ocr':
            markdown_text, error = pdf_to_markdown(temp_path)
        else:  # mode == 'direct'
            markdown_text, error = pdf_direct_to_markdown(temp_path)
            
        if error:
            return jsonify({'error': f'Failed to convert PDF to markdown: {error}'}), 400
        
        return jsonify({'markdown': markdown_text}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.route('/', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)), debug=True)