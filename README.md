# gcspdf2mdapi

An API that converts PDFs stored in Google Cloud Storage to Markdown format using OCR or direct text extraction.

## Overview

**gcspdf2mdapi** is a Flask-based API service that converts PDF documents stored in Google Cloud Storage to Markdown format. It offers two conversion methods:

1. **OCR-based conversion**: Uses Tesseract OCR via pytesseract to extract text from PDF pages rendered as images. This method is helpful for scanned documents or PDFs with text embedded in images.

2. **Direct text extraction**: Leverages PyMuPDF (fitz) and pymupdf4llm to extract text content directly from PDF documents while preserving structure.

Key technologies used:
- **Flask**: Web framework for the API endpoints
- **PyMuPDF**: PDF parsing and rendering
- **pymupdf4llm**: Converts PDF content to structured markdown
- **pytesseract & Pillow**: OCR processing
- **Google Cloud Storage**: For accessing PDF documents

The API is containerized using Docker and can be deployed to any container-supporting environment.

## Usage

The API provides endpoints to convert PDF files stored in Google Cloud Storage to Markdown format.

### Endpoints

#### Convert PDF to Markdown
```
POST /convert
```

**Request body:**
```json
{
  "file": "gs://bucket-name/path/to/file.pdf",
  "mode": "ocr|direct"
}
```

Parameters:
- `file`: GCS path to the PDF file (must start with `gs://`)
- `mode`: (Optional) Conversion method
  - `ocr`: Uses Optical Character Recognition (default)
  - `direct`: Uses direct text extraction

**Response:**
```json
{
  "markdown": "Extracted markdown content..."
}
```

#### Health Check
```
GET /
```

Returns API status:
```json
{
  "status": "ok"
}
```

### Examples

**Convert using OCR (default):**
```bash
curl -X POST https://your-api-endpoint/convert \
  -H "Content-Type: application/json" \
  -d '{"file": "gs://my-bucket/documents/report.pdf"}'
```

**Convert using direct text extraction:**
```bash
curl -X POST https://your-api-endpoint/convert \
  -H "Content-Type: application/json" \
  -d '{"file": "gs://my-bucket/documents/report.pdf", "mode": "direct"}'
```
