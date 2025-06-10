# config/secure_config.py
"""
SECURE CONFIG LOADER - Load secrets từ encrypted storage
THAY THẾ config/security.py cũ
"""
import os
import json
import base64
from pathlib import Path
from typing import Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from crypto.hsm_integration import HSMAdapter
import logging

logger = logging.getLogger(__name__)

class SecureConfig:
    """Production-ready secure configuration loader"""
    def _get_master_key_from_hsm(self):
        hsm = HSMAdapter()
        return hsm.get_master_key()
    
    def __init__(self):
        self.app_env = os.getenv("APP_ENV", "development")
        self.secrets_dir = Path("secrets")
        self._fernet = None
        self._secrets_cache = {}
        
        # Khởi tạo encryption nếu có secrets directory
        if self.secrets_dir.exists():
            self._init_encryption()
            self._load_encrypted_secrets()
    
    def _init_encryption(self):
        """Khởi tạo encryption từ master password"""
        # Lấy master password từ environment
        master_password = os.getenv("MASTER_PASSWORD")
        if not master_password:
            if self.app_env == "production":
                raise ValueError("MASTER_PASSWORD environment variable required in production!")
            else:
                logger.warning("No MASTER_PASSWORD set, using development mode")
                return
        
        try:
            # Đọc salt
            salt_file = self.secrets_dir / "salt.dat"
            if not salt_file.exists():
                raise FileNotFoundError("Salt file not found - run setup_production_secrets.py first")
            
            with open(salt_file, "rb") as f:
                salt = f.read()
            
            # Recreate encryption key
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            
            key = base64.urlsafe_b64encode(kdf.derive(master_password.encode()))
            self._fernet = Fernet(key)
            
            logger.info("✅ Encryption initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize encryption: {e}")
            if self.app_env == "production":
                raise
    
    def _load_encrypted_secrets(self):
        """Load và decrypt tất cả secrets"""
        if not self._fernet:
            return
        
        try:
            secrets_file = self.secrets_dir / "encrypted_secrets.json"
            if not secrets_file.exists():
                logger.warning("No encrypted secrets file found")
                return
            
            with open(secrets_file, "r") as f:
                encrypted_secrets = json.load(f)
            
            # Decrypt tất cả secrets
            for key, encrypted_value in encrypted_secrets.items():
                try:
                    decrypted = self._fernet.decrypt(encrypted_value.encode()).decode()
                    self._secrets_cache[key] = decrypted
                except Exception as e:
                    logger.error(f"Failed to decrypt secret '{key}': {e}")
            
            logger.info(f"✅ Loaded {len(self._secrets_cache)} encrypted secrets")
            
        except Exception as e:
            logger.error(f"❌ Failed to load encrypted secrets: {e}")
    
    def get_secret(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Lấy secret - ưu tiên encrypted, fallback to env"""
        # 1. Thử từ encrypted cache trước
        if key in self._secrets_cache:
            return self._secrets_cache[key]
        
        # 2. Fallback to environment variable
        env_value = os.getenv(key.upper())
        if env_value:
            return env_value
        
        # 3. Return default
        return default
    
    # Database Configuration
    @property
    def database_url(self) -> str:
        """Get database URL with encrypted password"""
        db_host = os.getenv("DB_HOST", "localhost")
        db_port = os.getenv("DB_PORT", "5432")
        db_name = os.getenv("DB_NAME", "quantum_commerce")
        db_user = os.getenv("DB_USER", "quantum_user")
        
        # Password từ encrypted storage
        db_password = self.get_secret("database_password")
        if not db_password:
            raise ValueError("Database password not found in encrypted secrets")
        
        return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    
    @property
    def redis_url(self) -> str:
        """Get Redis URL with encrypted password"""
        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = os.getenv("REDIS_PORT", "6379")
        
        redis_password = self.get_secret("redis_password")
        if redis_password:
            return f"redis://:{redis_password}@{redis_host}:{redis_port}"
        else:
            return f"redis://{redis_host}:{redis_port}"
    
    # Crypto Keys
    @property
    def jwt_secret(self) -> str:
        """Get JWT secret key"""
        secret = self.get_secret("jwt_secret")
        if not secret:
            raise ValueError("JWT secret not found - run setup_production_secrets.py")
        return secret
    
    @property
    def dilithium_master_key(self) -> str:
        """Get Dilithium master key"""
        key = self.get_secret("dilithium_master_key")
        if not key:
            raise ValueError("Dilithium master key not found")
        return key
    
    @property
    def ibe_master_key(self) -> str:
        """Get IBE master key"""
        key = self.get_secret("ibe_master_key")
        if not key:
            raise ValueError("IBE master key not found")
        return key
    
    @property
    def database_encryption_key(self) -> bytes:
        """Get database field encryption key"""
        key_str = self.get_secret("database_encryption_key")
        if not key_str:
            raise ValueError("Database encryption key not found")
        return base64.b64decode(key_str)
    
    # App Configuration
    @property
    def app_env(self) -> str:
        return self._app_env
    
    @app_env.setter
    def app_env(self, value: str):
        self._app_env = value
    
    @property
    def debug(self) -> bool:
        return os.getenv("DEBUG", "false").lower() == "true"
    
    @property
    def use_real_crypto(self) -> bool:
        return os.getenv("USE_REAL_CRYPTO", "true").lower() == "true"
    
    # Security Settings
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRATION_HOURS = 24
    SESSION_TIMEOUT_MINUTES = int(os.getenv("SESSION_TIMEOUT_MINUTES", "30"))
    
    # Rate Limiting
    RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    
    def validate_config(self):
        """Validate tất cả required configs"""
        required_secrets = [
            "jwt_secret",
            "dilithium_master_key", 
            "ibe_master_key",
            "database_password"
        ]
        
        missing = []
        for secret in required_secrets:
            if not self.get_secret(secret):
                missing.append(secret)
        
        if missing:
            if self.app_env == "production":
                raise ValueError(f"Missing required secrets: {missing}")
            else:
                logger.warning(f"Missing secrets in development: {missing}")
        
        logger.info("✅ Configuration validation passed")

# Global config instance
config = SecureConfig()

# Backward compatibility
class SecurityConfig:
    """Backward compatibility wrapper"""
    
    @staticmethod
    def get_database_url() -> str:
        return config.database_url
    
    @staticmethod
    def get_redis_url() -> str:
        return config.redis_url
    
    @staticmethod
    def get_jwt_secret() -> str:
        return config.jwt_secret
    
    @staticmethod
    def get_dilithium_key() -> str:
        return config.dilithium_master_key
    
    @staticmethod
    def get_ibe_key() -> str:
        return config.ibe_master_key
    
    @staticmethod
    def validate():
        return config.validate_config()
    
    # Constants
    APP_ENV = config.app_env
    JWT_ALGORITHM = config.JWT_ALGORITHM
    JWT_EXPIRATION_HOURS = config.JWT_EXPIRATION_HOURS