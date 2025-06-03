FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install additional missing packages
RUN pip install --no-cache-dir \
    PyJWT==2.8.0 \
    python-jose[cryptography]==3.3.0 \
    email-validator==2.0.0 \
    python-multipart==0.0.6 \
    psycopg2-binary==2.9.7

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p keys/ibe keys/dilithium logs

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# Create start script
RUN echo '#!/bin/sh\nuvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}' > /app/start.sh
RUN chmod +x /app/start.sh

# Use shell form to expand environment variables
CMD ["/bin/sh", "/app/start.sh"]
