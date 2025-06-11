FROM python:3.12-slim

# Cài đặt gói hệ thống cần thiết
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Tạo thư mục làm việc
WORKDIR /app

# Copy và cài đặt phụ thuộc Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Cài thêm các gói phụ nếu chưa có trong requirements.txt
RUN pip install --no-cache-dir \
    PyJWT==2.8.0 \
    python-jose[cryptography]==3.3.0 \
    email-validator==2.0.0 \
    python-multipart==0.0.6 \
    psycopg2-binary==2.9.7 \
    uvicorn[standard]==0.29.0

# Copy toàn bộ mã nguồn
COPY . .

# Tạo các thư mục cần thiết
RUN mkdir -p keys/ibe keys/dilithium logs secrets

# Mở cổng 8000
EXPOSE 8000

# Chạy ứng dụng bằng Uvicorn (FastAPI/ASGI)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
