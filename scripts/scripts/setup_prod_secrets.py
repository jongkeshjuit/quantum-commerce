#!/usr/bin/env python3
"""
PRODUCTION SECRET SETUP - SECURE KEY MANAGEMENT
Tạo và quản lý secrets an toàn cho production
setup_prodution_secrets.py
"""
import os
import json
import base64
import secrets
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class ProductionSecretManager:
    """Quản lý secrets cho production environment"""
    
    def __init__(self):
        self.secrets_dir = Path("secrets")
        self.secrets_dir.mkdir(exist_ok=True)
        
        # Bảo vệ thư mục secrets
        os.chmod(self.secrets_dir, 0o700)
        
    def generate_master_key(self) -> bytes:
        """Tạo master key từ password"""
        print("🔐 THIẾT LẬP MASTER KEY PRODUCTION")
        print("=" * 50)
        
        # Lấy master password từ người dùng
        master_password = os.getenv("MASTER_PASSWORD")
        if not master_password:
            master_password = input("Nhập MASTER_PASSWORD (sẽ lưu trong ENV): ")
            print("\n⚠️  LƯU MASTER_PASSWORD VÀO ENVIRONMENT VARIABLE:")
            print(f"export MASTER_PASSWORD='{master_password}'")
            print("hoặc thêm vào .env file (KHÔNG commit .env!)")
        
        # Tạo salt ngẫu nhiên
        salt = os.urandom(16)
        
        # Derive key với PBKDF2
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,  # 100k iterations cho security
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(master_password.encode()))
        
        # Lưu salt
        salt_file = self.secrets_dir / "salt.dat"
        with open(salt_file, "wb") as f:
            f.write(salt)
        os.chmod(salt_file, 0o600)
        
        print(f"✅ Master key generated với 100,000 PBKDF2 iterations")
        print(f"✅ Salt saved to {salt_file}")
        
        return key
    
    def create_production_secrets(self):
        """Tạo tất cả secrets cần thiết cho production"""
        print("\n🔑 TẠO PRODUCTION SECRETS")
        print("=" * 40)
        
        # Generate master key
        master_key = self.generate_master_key()
        fernet = Fernet(master_key)
        
        # Generate secure secrets
        secrets_to_create = {
            'jwt_secret': base64.b64encode(secrets.token_bytes(32)).decode(),
            'dilithium_master_key': base64.b64encode(secrets.token_bytes(64)).decode(),
            'ibe_master_key': base64.b64encode(secrets.token_bytes(32)).decode(),
            'database_encryption_key': base64.b64encode(secrets.token_bytes(32)).decode(),
            'database_password': self._generate_secure_password(16),
            'redis_password': self._generate_secure_password(12),
        }
        
        # Encrypt và lưu secrets
        encrypted_secrets = {}
        for key, value in secrets_to_create.items():
            encrypted_value = fernet.encrypt(value.encode()).decode()
            encrypted_secrets[key] = encrypted_value
            print(f"✅ Generated: {key}")
        
        # Lưu encrypted secrets file
        secrets_file = self.secrets_dir / "encrypted_secrets.json"
        with open(secrets_file, "w") as f:
            json.dump(encrypted_secrets, f, indent=2)
        os.chmod(secrets_file, 0o600)
        
        print(f"\n✅ Encrypted secrets saved to {secrets_file}")
        print(f"🔒 File permissions: 600 (owner only)")
        
        return encrypted_secrets
    
    def _generate_secure_password(self, length: int) -> str:
        """Tạo password mạnh"""
        import string
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    def validate_secrets(self):
        """Kiểm tra tất cả secrets có tồn tại không"""
        print("\n🔍 KIỂM TRA SECRETS")
        print("=" * 30)
        
        required_secrets = [
            'jwt_secret',
            'dilithium_master_key', 
            'ibe_master_key',
            'database_encryption_key',
            'database_password',
            'redis_password'
        ]
        
        from services.secret_manager import secret_manager
        
        missing = []
        for secret in required_secrets:
            value = secret_manager.get_secret(secret)
            if value:
                print(f"✅ {secret}: {'*' * 20}")
            else:
                print(f"❌ {secret}: MISSING")
                missing.append(secret)
        
        if missing:
            print(f"\n⚠️  THIẾU SECRETS: {missing}")
            return False
        else:
            print(f"\n🎉 TẤT CẢ SECRETS ĐÃ SẴN SÀNG!")
            return True
    
    def setup_gitignore(self):
        """Tạo .gitignore để bảo vệ secrets"""
        gitignore_content = """
# SECRETS - KHÔNG BAO GIỜ COMMIT!
secrets/
.env
.env.local
.env.production
*.key
*.pem

# Crypto keys
keys/dilithium/
keys/ibe/
dilithium_*.key
ibe_*.key

# Database
*.db
*.sqlite

# Logs có thể chứa sensitive data
logs/
*.log

# Docker secrets
docker-compose.override.yml
.docker/

# Backup files
*.bak
*.backup
"""
        
        gitignore_file = Path(".gitignore")
        if gitignore_file.exists():
            with open(gitignore_file, "a") as f:
                f.write(gitignore_content)
        else:
            with open(gitignore_file, "w") as f:
                f.write(gitignore_content)
        
        print("✅ Updated .gitignore để bảo vệ secrets")
    
    def production_deployment_guide(self):
        """Hướng dẫn deploy production"""
        print("\n🚀 HƯỚNG DẪN DEPLOY PRODUCTION")
        print("=" * 50)
        
        guide = """
1. 🔐 THIẾT LẬP SECRETS:
   - Set MASTER_PASSWORD trong environment
   - Copy secrets/ folder lên server (SCP/SFTP)
   - chmod 700 secrets/
   - chmod 600 secrets/*

2. 🛡️  PRODUCTION ENVIRONMENT:
   export APP_ENV=production
   export MASTER_PASSWORD='your_secure_master_password'
   export USE_REAL_CRYPTO=true

3. 🗄️  DATABASE SETUP:
   - Tạo PostgreSQL database
   - Set DB_PASSWORD từ secrets
   - Run migrations: python scripts/create_tables.py

4. 🔧 INFRASTRUCTURE:
   - Setup HashiCorp Vault cho enterprise
   - Configure HSM nếu có
   - Setup load balancer
   - Configure monitoring

5. 🚀 DEPLOYMENT:
   docker-compose -f docker-compose.production.yml up -d

6. ✅ VERIFY:
   python scripts/test_real_crypto.py
   curl http://localhost:8000/api/crypto/status
        """
        
        print(guide)

if __name__ == "__main__":
    print("🛡️  QUANTUM-SECURE E-COMMERCE")
    print("🔐 PRODUCTION SECRET MANAGER")
    print("=" * 60)
    
    manager = ProductionSecretManager()
    
    # Setup menu
    while True:
        print("\nTùy chọn:")
        print("1. 🔑 Tạo production secrets")
        print("2. 🔍 Kiểm tra secrets hiện tại")
        print("3. 📝 Setup .gitignore")
        print("4. 📋 Hướng dẫn deployment")
        print("5. 🚪 Thoát")
        
        choice = input("\nChọn (1-5): ").strip()
        
        if choice == "1":
            manager.create_production_secrets()
            manager.setup_gitignore()
        elif choice == "2":
            manager.validate_secrets()
        elif choice == "3":
            manager.setup_gitignore()
        elif choice == "4":
            manager.production_deployment_guide()
        elif choice == "5":
            print("👋 Bye!")
            break
        else:
            print("❌ Lựa chọn không hợp lệ")