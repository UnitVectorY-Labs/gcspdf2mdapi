# Use the official Python image
FROM python:3.13

# Install Tesseract-OCR (required for pytesseract)
RUN apt-get update && apt-get install -y tesseract-ocr

# Set the working directory inside the container
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Python script
COPY pdf2md.py /app/pdf2md.py

# Expose the port the app runs on
EXPOSE 8080

# Set the default command to run the API server
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "pdf2md:app"]
