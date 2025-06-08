# scripts/setup_production_secrets.py
"""
PRODUCTION SECRET SETUP - KHÔNG BAO GIỜ commit file này
Chạy 1 lần duy nhất để setup secrets, sau đó XÓA
"""
import os
import base64
import secrets
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class ProductionSecretSetup:
    """Setup secrets cho production - CHỈ CHẠY 1 LẦN"""
    
    def __init__(self):
        self.secrets_dir = Path("secrets")
        self.secrets_dir.mkdir(mode=0o700, exist_ok=True)
        
        # ĐỌC master password từ KEYBOARD (không lưu file)
        self.master_password = input("Nhập MASTER PASSWORD (nhớ kỹ, không lưu đâu): ").encode()
        
        # Tạo encryption key từ password
        salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        
        self.key = base64.urlsafe_b64encode(kdf.derive(self.master_password))
        self.fernet = Fernet(self.key)
        
        # Lưu salt (cần để decrypt sau này)
        with open(self.secrets_dir / "salt.dat", "wb") as f:
            f.write(salt)
        os.chmod(self.secrets_dir / "salt.dat", 0o600)
    
    def generate_crypto_keys(self):
        """Tạo REAL crypto keys"""
        print("🔑 Generating cryptographic keys...")
        
        # 1. JWT Secret (256-bit)
        jwt_secret = base64.b64encode(secrets.token_bytes(32)).decode()
        
        # 2. Dilithium Master Key (512-bit for high security)
        dilithium_key = base64.b64encode(secrets.token_bytes(64)).decode()
        
        # 3. IBE Master Key (256-bit)
        ibe_key = base64.b64encode(secrets.token_bytes(32)).decode()
        
        # 4. Database encryption key
        db_key = base64.b64encode(secrets.token_bytes(32)).decode()
        
        # 5. Redis password
        redis_pass = secrets.token_urlsafe(32)
        
        # 6. Database password  
        db_pass = secrets.token_urlsafe(24)
        
        return {
            "jwt_secret": jwt_secret,
            "dilithium_master_key": dilithium_key,
            "ibe_master_key": ibe_key,
            "database_encryption_key": db_key,
            "redis_password": redis_pass,
            "database_password": db_pass,
        }
    
    def encrypt_and_store_secrets(self, secrets_dict):
        """Mã hóa và lưu secrets"""
        print("🔒 Encrypting and storing secrets...")
        
        encrypted_secrets = {}
        for key, value in secrets_dict.items():
            encrypted_value = self.fernet.encrypt(value.encode()).decode()
            encrypted_secrets[key] = encrypted_value
        
        # Lưu vào file mã hóa
        import json
        with open(self.secrets_dir / "encrypted_secrets.json", "w") as f:
            json.dump(encrypted_secrets, f, indent=2)
        
        os.chmod(self.secrets_dir / "encrypted_secrets.json", 0o600)
        
        print("✅ Secrets encrypted and stored safely")
    
    def create_env_template(self):
        """Tạo .env template KHÔNG chứa secrets"""
        template = """# .env.production
# PRODUCTION ENVIRONMENT - NO SECRETS HERE!
# All secrets are stored encrypted in secrets/ directory

# Application Config
APP_NAME=quantum-commerce
APP_ENV=production
DEBUG=false

# Database Connection (passwords stored encrypted)
DB_HOST=postgres
DB_PORT=5432
DB_NAME=quantum_commerce
DB_USER=qsc_user

# Redis Connection  
REDIS_HOST=redis
REDIS_PORT=6379

# Vault Config
VAULT_ADDR=http://vault:8200

# Feature Flags
USE_REAL_CRYPTO=true
RATE_LIMIT_ENABLED=true
SESSION_TIMEOUT_MINUTES=30

# Monitoring
PROMETHEUS_PORT=9090
GRAFANA_PORT=3030

# ⚠️ SECRETS ĐƯỢC LẤY TỪ ENCRYPTED STORAGE
# KHÔNG BAO GIỜ commit passwords vào đây!
"""
        
        with open(".env.production", "w") as f:
            f.write(template)
        
        print("📝 Created .env.production template")
    
    def setup_gitignore(self):
        """Cập nhật .gitignore để bảo vệ secrets"""
        gitignore_additions = """
# SECURITY - NEVER COMMIT THESE!
secrets/
.env
.env.local
.env.production
.env.development
*.key
*.pem
master_password.txt
vault_token.txt

# Crypto keys
keys/dilithium/
keys/ibe/
keys/*.key

# Logs có thể chứa sensitive data
logs/*.log
logs/security.log

# Database dumps
*.sql
*.db

# Backup files
*.backup
*.bak
temp/
"""
        
        with open(".gitignore", "a") as f:
            f.write(gitignore_additions)
        
        print("🛡️ Updated .gitignore for security")
    
    def run_setup(self):
        """Chạy toàn bộ setup"""
        print("🚀 PRODUCTION SECRET SETUP")
        print("=" * 50)
        
        # 1. Generate keys
        secrets_dict = self.generate_crypto_keys()
        
        # 2. Encrypt and store
        self.encrypt_and_store_secrets(secrets_dict)
        
        # 3. Create templates
        self.create_env_template()
        
        # 4. Setup gitignore
        self.setup_gitignore()
        
        print("\n✅ SETUP COMPLETE!")
        print("🔑 Secrets stored encrypted in secrets/")
        print("⚠️  NHỚ MASTER PASSWORD - không có cách nào recover!")
        print("📝 Sử dụng .env.production template")
        
        # Hiển thị hướng dẫn
        print("\n📋 NEXT STEPS:")
        print("1. Export MASTER_PASSWORD environment variable")
        print("2. rm scripts/setup_production_secrets.py  # XÓA FILE NÀY!")
        print("3. git add .gitignore")
        print("4. git commit -m 'Add security .gitignore'")
        print("5. KHÔNG BAO GIỜ commit secrets/")

if __name__ == "__main__":
    setup = ProductionSecretSetup()
    setup.run_setup()