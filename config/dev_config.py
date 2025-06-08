
import os

class SecurityConfig:
    APP_ENV = "development"
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRATION_HOURS = 24
    SESSION_TIMEOUT_MINUTES = 30
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
    DILITHIUM_MASTER_KEY = "dev_dilithium_key_123"
    IBE_MASTER_KEY = "dev_ibe_key_123"
    @staticmethod
    def get_jwt_secret():
        return os.getenv("JWT_SECRET", "dev_jwt_secret_123")
    
    @staticmethod
    def get_database_url():
        return os.getenv("DATABASE_URL", "sqlite:///./quantum_commerce_dev.db")
    
    @staticmethod
    def get_redis_url():
        return os.getenv("REDIS_URL", "redis://localhost:6379")
    
    @staticmethod
    def get_fernet_key():
        from cryptography.fernet import Fernet
        return Fernet.generate_key()
    
    @staticmethod
    def validate():
        print("✅ Development config loaded")
        return True

config = SecurityConfig()
