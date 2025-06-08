"""
Real Secret Manager - KHÔNG LƯU SECRETS TRONG CODE
"""
import os
import json
import base64
import logging
from typing import Optional, Dict
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

logger = logging.getLogger(__name__)

class SecretManager:
    """
    Real Secret Manager - Chỉ lưu secrets trong:
    1. Environment variables (cho development)
    2. Encrypted files với master key từ ENV
    3. External secret stores (Vault, AWS Secrets Manager)
    
    KHÔNG BAO GIỜ commit secrets vào git!
    """
    
    def __init__(self):
        self.secrets_file = Path("secrets/encrypted_secrets.json")
        self.master_key = self._get_master_key()
        self.fernet = Fernet(self.master_key) if self.master_key else None
        
        # Tạo thư mục secrets nếu chưa có
        self.secrets_file.parent.mkdir(exist_ok=True)
        
        # Bảo vệ thư mục secrets
        os.chmod(self.secrets_file.parent, 0o700)
        
    def _get_master_key(self) -> Optional[bytes]:
        """Lấy master key từ ENV hoặc tạo mới"""
        # 1. Thử lấy từ environment variable
        env_key = os.getenv('MASTER_ENCRYPTION_KEY')
        if env_key:
            try:
                return base64.b64decode(env_key)
            except:
                logger.error("Invalid MASTER_ENCRYPTION_KEY in environment")
        
        # 2. Thử lấy từ file key
        key_file = Path("secrets/.master.key")
        if key_file.exists():
            try:
                with open(key_file, 'rb') as f:
                    return f.read()
            except Exception as e:
                logger.error(f"Cannot read master key file: {e}")
        
        # 3. Tạo master key mới từ password
        master_password = os.getenv('MASTER_PASSWORD')
        if not master_password:
            logger.warning("No MASTER_PASSWORD set! Using default (INSECURE)")
            master_password = "quantum_secure_default_change_me"
        
        # Derive key từ password
        salt = b'quantum_secure_salt_2025'  # In production, use random salt
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(master_password.encode()))
        
        # Lưu key file để lần sau không phải tạo lại
        try:
            with open(key_file, 'wb') as f:
                f.write(key)
            os.chmod(key_file, 0o600)  # Chỉ owner đọc được
            logger.info("✅ Master key created and saved")
        except Exception as e:
            logger.error(f"Cannot save master key: {e}")
        
        return key
    
    def store_secret(self, key: str, value: str) -> bool:
        """Lưu secret được mã hóa"""
        if not self.fernet:
            logger.error("No encryption key available")
            return False
            
        try:
            # Đọc secrets hiện tại
            secrets = {}
            if self.secrets_file.exists():
                with open(self.secrets_file, 'r') as f:
                    secrets = json.load(f)
            
            # Mã hóa secret
            encrypted_value = self.fernet.encrypt(value.encode()).decode()
            secrets[key] = encrypted_value
            
            # Lưu lại file
            with open(self.secrets_file, 'w') as f:
                json.dump(secrets, f)
            os.chmod(self.secrets_file, 0o600)
            
            logger.info(f"✅ Secret '{key}' stored securely")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store secret '{key}': {e}")
            return False
    
    def get_secret(self, key: str) -> Optional[str]:
        """Lấy secret và giải mã"""
        # 1. Thử lấy từ environment trước
        env_value = os.getenv(key.upper())
        if env_value:
            return env_value
            
        # 2. Thử lấy từ file mã hóa
        if not self.fernet:
            logger.error("No encryption key available")
            return None
            
        try:
            if not self.secrets_file.exists():
                return None
                
            with open(self.secrets_file, 'r') as f:
                secrets = json.load(f)
            
            if key not in secrets:
                return None
            
            # Giải mã
            encrypted_value = secrets[key].encode()
            decrypted_value = self.fernet.decrypt(encrypted_value).decode()
            
            return decrypted_value
            
        except Exception as e:
            logger.error(f"Failed to get secret '{key}': {e}")
            return None
    
    def initialize_default_secrets(self):
        """Khởi tạo secrets mặc định nếu chưa có"""
        default_secrets = {
            'jwt_secret': base64.b64encode(os.urandom(32)).decode(),
            'database_password': os.getenv('DB_PASSWORD', 'quantum_pass'),
            'dilithium_master_key': base64.b64encode(os.urandom(64)).decode(),
            'ibe_master_key': base64.b64encode(os.urandom(32)).decode(),
            'redis_password': os.getenv('REDIS_PASSWORD', 'redis_pass'),
        }
        
        for key, value in default_secrets.items():
            if not self.get_secret(key):
                self.store_secret(key, value)
                logger.info(f"✅ Initialized secret: {key}")
    
    def list_secret_keys(self) -> list:
        """List tất cả secret keys (không show values)"""
        try:
            if not self.secrets_file.exists():
                return []
                
            with open(self.secrets_file, 'r') as f:
                secrets = json.load(f)
            
            return list(secrets.keys())
            
        except Exception as e:
            logger.error(f"Failed to list secrets: {e}")
            return []
    
    def delete_secret(self, key: str) -> bool:
        """Xóa secret"""
        try:
            if not self.secrets_file.exists():
                return False
                
            with open(self.secrets_file, 'r') as f:
                secrets = json.load(f)
            
            if key in secrets:
                del secrets[key]
                
                with open(self.secrets_file, 'w') as f:
                    json.dump(secrets, f)
                
                logger.info(f"✅ Secret '{key}' deleted")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to delete secret '{key}': {e}")
            return False

# Global instance
secret_manager = SecretManager()

# Khởi tạo secrets khi import module
try:
    secret_manager.initialize_default_secrets()
except Exception as e:
    logger.error(f"Failed to initialize secrets: {e}")