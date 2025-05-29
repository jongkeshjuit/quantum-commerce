# 🔐 Quantum-Secure E-Commerce System

Hệ thống thương mại điện tử bảo mật hậu lượng tử sử dụng Identity-Based Encryption (IBE) và CRYSTALS-Dilithium digital signatures.

## 🌟 Tính năng

- **🔒 Mã hóa IBE**: Mã hóa dựa trên danh tính, không cần quản lý chứng chỉ phức tạp
- **✍️ Chữ ký Dilithium**: Chữ ký số kháng lượng tử theo chuẩn NIST
- **💳 Xử lý thanh toán an toàn**: Hỗ trợ nhiều phương thức thanh toán
- **🔍 Xác minh giao dịch**: Kiểm tra tính toàn vẹn của mọi giao dịch
- **📄 Hóa đơn mã hóa**: Tạo và lưu trữ hóa đơn được mã hóa
- **🔑 Quản lý khóa tự động**: Xoay khóa và thu hồi danh tính

## 📋 Yêu cầu hệ thống

- Python 3.9+
- Docker & Docker Compose
- PostgreSQL 15+
- Redis 7+
- Node.js 16+ (cho frontend)
- OpenSSL

## 🚀 Cài đặt nhanh

### 1. Clone repository

```bash
git clone https://github.com/yourproject/quantum-secure-commerce.git
cd quantum-secure-commerce
```

### 2. Chạy script setup tự động

```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

Script sẽ tự động:
- Tạo môi trường ảo Python
- Cài đặt dependencies
- Tạo cấu trúc thư mục
- Khởi tạo khóa mã hóa
- Setup database
- Cài đặt frontend

### 3. Cập nhật file môi trường

Mở file `.env` và cập nhật các mật khẩu:

```env
DB_PASSWORD=your_secure_password_here
REDIS_PASSWORD=your_redis_password_here
IBE_MASTER_PASSWORD=your_ibe_master_password
DILITHIUM_KEY_PASSWORD=your_key_password
```

### 4. Khởi động services

```bash
docker-compose up -d
```

## 🔧 Cài đặt thủ công

### 1. Cài đặt Python dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Cài đặt liboqs-python

```bash
# Ubuntu/Debian
sudo apt-get install cmake gcc libopenssl-dev

# macOS
brew install cmake openssl

# Cài đặt liboqs-python
pip install git+https://github.com/open-quantum-safe/liboqs-python.git
```

### 3. Khởi tạo hệ thống crypto

```bash
python scripts/init_crypto.py
```

### 4. Setup database

```bash
# Start PostgreSQL
docker run -d \
  --name qsc_postgres \
  -e POSTGRES_DB=quantum_commerce \
  -e POSTGRES_USER=qsc_user \
  -e POSTGRES_PASSWORD=secure_password \
  -p 5432:5432 \
  postgres:15-alpine

# Create schema
python scripts/setup_db.py
```

### 5. Chạy API server

```bash
python main.py
```

## 📚 Sử dụng API

### Authentication

#### Đăng ký user mới

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "name": "John Doe",
    "password": "secure_password",
    "user_type": "customer"
  }'
```

#### Đăng nhập

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "secure_password"
  }'
```

### Xử lý thanh toán

```bash
# Cần token từ login
export TOKEN="your_jwt_token_here"

curl -X POST http://localhost:8000/api/payments/process \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "amount": 99.99,
    "currency": "USD",
    "payment_method": "credit_card",
    "card_data": {
      "number": "4111111111111111",
      "exp_month": "12",
      "exp_year": "2025",
      "cvv": "123"
    },
    "billing_address": {
      "name": "John Doe",
      "street": "123 Main St",
      "city": "Anytown",
      "state": "CA",
      "zip": "12345"
    }
  }'
```

### Xác minh giao dịch

```bash
curl -X POST http://localhost:8000/api/payments/verify \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "transaction_id": "TXN123456",
    "signature": "signature_base64"
  }'
```

## 🏗️ Kiến trúc hệ thống

```
┌─────────────────────────────────────────────────────────────────┐
│                         Load Balancer (Nginx)                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    │
│  │   Frontend   │    │   API Server │    │   Admin UI   │    │
│  │   (React)    │    │  (FastAPI)   │    │  (Optional)  │    │
│  └──────────────┘    └──────────────┘    └──────────────┘    │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                      Security Layer                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    │
│  │     IBE      │    │  Dilithium   │    │     Key      │    │
│  │   Service    │    │   Service    │    │   Manager    │    │
│  └──────────────┘    └──────────────┘    └──────────────┘    │
├─────────────────────────────────────────────────────────────────┤
│                      Data Layer                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    │
│  │  PostgreSQL  │    │    Redis     │    │   File/HSM   │    │
│  │  (Database)  │    │   (Cache)    │    │   Storage    │    │
│  └──────────────┘    └──────────────┘    └──────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

## 🔐 Bảo mật

### Mã hóa IBE

- **Thuật toán**: Boneh-Franklin IBE với Elliptic Curves
- **Key size**: 256-bit
- **Ứng dụng**: Mã hóa dữ liệu thanh toán, receipts

### Chữ ký Dilithium

- **Thuật toán**: CRYSTALS-Dilithium (NIST PQC)
- **Security level**: NIST Level 2 (≈128-bit)
- **Signature size**: 2,420 bytes
- **Ứng dụng**: Ký giao dịch, tạo hóa đơn

### Best Practices

1. **Luôn sử dụng HTTPS** trong production
2. **Rotate keys định kỳ** (mặc định 90 ngày)
3. **Backup keys** trong HSM hoặc secure storage
4. **Monitor** mọi hoạt động crypto
5. **Update** libraries thường xuyên

## 🧪 Testing

### Unit tests

```bash
pytest tests/test_crypto.py -v
pytest tests/test_api.py -v
```

### Integration tests

```bash
pytest tests/test_integration.py -v
```

### Load testing

```bash
# Cài đặt locust
pip install locust

# Chạy load test
locust -f tests/load_test.py --host=http://localhost:8000
```

## 📊 Monitoring

### Prometheus metrics

API tự động export metrics tại `/metrics`:

- `payment_processing_time`
- `ibe_encryption_duration`
- `dilithium_signing_duration`
- `transaction_verification_rate`

### Logging

Logs được lưu trong thư mục `logs/`:

- `api.log`: API requests và responses
- `crypto.log`: Cryptographic operations
- `security.log`: Security events

## 🚨 Troubleshooting

### Lỗi: "liboqs not found"

```bash
# Cài đặt lại liboqs-python
pip uninstall liboqs-python
pip install git+https://github.com/open-quantum-safe/liboqs-python.git
```

### Lỗi: "Cannot connect to PostgreSQL"

```bash
# Kiểm tra PostgreSQL container
docker ps
docker logs qsc_postgres

# Restart nếu cần
docker-compose restart postgres
```

### Lỗi: "IBE key not found"

```bash
# Khởi tạo lại keys
python scripts/init_crypto.py --force
```

## 🤝 Contributing

1. Fork repository
2. Tạo feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Tạo Pull Request

## 📝 License

Dự án này được cấp phép theo MIT License - xem file [LICENSE](LICENSE) để biết chi tiết.

## 👥 Team

- **Lead Developer**: [Your Name]
- **Security Architect**: [Name]
- **Frontend Developer**: [Name]

## 📞 Support

- **Email**: support@quantumsecurecommerce.com
- **Documentation**: https://docs.quantumsecurecommerce.com
- **Issues**: https://github.com/yourproject/quantum-secure-commerce/issues

## 🔮 Roadmap

- [ ] Tích hợp HSM cho production
- [ ] Hỗ trợ multiple currencies
- [ ] Mobile SDK
- [ ] Blockchain integration
- [ ] Advanced fraud detection
- [ ] Multi-tenant support

---

**Note**: Đây là implementation demo cho mục đích học tập. Trong production, cần thêm nhiều security measures và optimizations.