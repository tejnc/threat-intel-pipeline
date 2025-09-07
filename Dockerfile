# Dockerfile
FROM python:3.11-slim

# Install system deps for PDFs
RUN apt-get update && apt-get install -y \
    libpoppler-cpp-dev \
    tesseract-ocr \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set workdir
WORKDIR /app

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY src/ ./src
COPY data/ ./data

# Expose FastAPI port
EXPOSE 8000

# Default run
# CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]
