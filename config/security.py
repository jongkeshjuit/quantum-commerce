# config/security.py
"""
Centralized security configuration
"""
import os
import secrets
from typing import Optional
from dotenv import load_dotenv
from cryptography.fernet import Fernet
import logging

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class SecurityConfig:
    """Security configuration management"""
    
    # Application
    APP_ENV = os.getenv('APP_ENV', 'development')
    APP_DEBUG = os.getenv('APP_DEBUG', 'false').lower() == 'true'
    
    # Security Keys
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    DILITHIUM_MASTER_KEY = os.getenv('DILITHIUM_MASTER_KEY')
    IBE_MASTER_KEY = os.getenv('IBE_MASTER_KEY')
    DATABASE_ENCRYPTION_KEY = os.getenv('DATABASE_ENCRYPTION_KEY')
    
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL')
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
    
    # External Services
    VAULT_ADDR = os.getenv('VAULT_ADDR')
    VAULT_TOKEN = os.getenv('VAULT_TOKEN')
    
    # Security Settings
    BCRYPT_ROUNDS = 12
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRATION_HOURS = 24
    SESSION_TIMEOUT_MINUTES = 30
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION_MINUTES = 15
    
    @classmethod
    def validate(cls) -> bool:
        """Validate all required secrets are set"""
        required_keys = [
            'JWT_SECRET_KEY',
            'DILITHIUM_MASTER_KEY', 
            'IBE_MASTER_KEY',
            'DATABASE_ENCRYPTION_KEY',
            'DATABASE_URL'
        ]
        
        missing_keys = []
        for key in required_keys:
            if not getattr(cls, key):
                missing_keys.append(key)
        
        if missing_keys:
            logger.error(f"Missing required configuration keys: {missing_keys}")
            if cls.APP_ENV == 'production':
                raise ValueError(f"Missing required configuration: {missing_keys}")
            else:
                logger.warning("Running in development mode with missing keys")
                cls._generate_dev_keys()
        
        return len(missing_keys) == 0
    
    @classmethod
    def _generate_dev_keys(cls):
        """Generate development keys (NEVER use in production)"""
        if cls.APP_ENV != 'development':
            raise RuntimeError("Cannot generate keys in production")
        
        logger.warning("GENERATING DEVELOPMENT KEYS - DO NOT USE IN PRODUCTION")
        
        if not cls.JWT_SECRET_KEY:
            cls.JWT_SECRET_KEY = secrets.token_urlsafe(32)
        if not cls.DILITHIUM_MASTER_KEY:
            cls.DILITHIUM_MASTER_KEY = secrets.token_urlsafe(64)
        if not cls.IBE_MASTER_KEY:
            cls.IBE_MASTER_KEY = secrets.token_urlsafe(32)
        if not cls.DATABASE_ENCRYPTION_KEY:
            cls.DATABASE_ENCRYPTION_KEY = Fernet.generate_key().decode()
    
    @classmethod
    def get_fernet_key(cls) -> bytes:
        """Get Fernet key for database encryption"""
        if not cls.DATABASE_ENCRYPTION_KEY:
            raise ValueError("DATABASE_ENCRYPTION_KEY not set")
        
        # Ensure it's a valid Fernet key
        if len(cls.DATABASE_ENCRYPTION_KEY) == 44:  # Base64 encoded 32 bytes
            return cls.DATABASE_ENCRYPTION_KEY.encode()
        else:
            # Generate a proper key from the provided secret
            import hashlib
            import base64
            digest = hashlib.sha256(cls.DATABASE_ENCRYPTION_KEY.encode()).digest()
            return base64.urlsafe_b64encode(digest)

# Initialize and validate on import
SecurityConfig.validate()