
# config/development_config.py - Sử dụng raw secrets từ .env
import os

class SecurityConfig:
    APP_ENV = os.getenv("ENVIRONMENT", "development")
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRATION_HOURS = 24
    SESSION_TIMEOUT_MINUTES = 30
    
    @staticmethod
    def get_jwt_secret():
        return os.getenv("JWT_SECRET", "dev_jwt_fallback")
    
    @staticmethod
    def get_database_url():
        return os.getenv("DATABASE_URL", "sqlite:///./quantum_commerce_dev.db")
    
    @staticmethod
    def get_redis_url():
        return os.getenv("REDIS_URL", "redis://localhost:6379")
    
    @staticmethod
    def get_fernet_key():
        from cryptography.fernet import Fernet
        key = os.getenv("FERNET_KEY")
        return key.encode() if key else Fernet.generate_key()
    
    @staticmethod
    def validate():
        print("✅ Using development config with raw secrets")
        return True

    # Properties for compatibility
    REDIS_URL = get_redis_url.__func__()

config = SecurityConfig()
