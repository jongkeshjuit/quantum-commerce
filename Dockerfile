FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install additional packages
RUN pip install --no-cache-dir \
    PyJWT==2.8.0 \
    python-jose[cryptography]==3.3.0 \
    email-validator==2.0.0 \
    python-multipart==0.0.6 \
    psycopg2-binary==2.9.7

# Copy application
COPY . .

# Create directories
RUN mkdir -p keys/ibe keys/dilithium logs secrets

# Expose port
EXPOSE 8000

# Run command
CMD ["python", "main.py"]
