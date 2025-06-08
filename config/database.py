"""
Database configuration
"""
import os
from typing import Optional

class DatabaseConfig:
    """Database configuration settings"""
    
    # Database settings
    DB_HOST: str = os.getenv('DB_HOST', 'localhost')
    DB_PORT: int = int(os.getenv('DB_PORT', '5432'))
    DB_NAME: str = os.getenv('DB_NAME', 'quantum_commerce')
    DB_USER: str = os.getenv('DB_USER', 'qsc_user')
    DB_PASSWORD: str = os.getenv('DB_PASSWORD', 'secure_password')
    
    # Connection settings
    DATABASE_ECHO: bool = os.getenv('DATABASE_ECHO', 'false').lower() == 'true'
    MAX_CONNECTIONS: int = int(os.getenv('MAX_CONNECTIONS', '20'))
    
    @classmethod
    def get_database_url(cls) -> str:
        """Get database connection URL"""
        return f"postgresql://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"
    
    @classmethod
    def get_sqlite_url(cls) -> str:
        """Get SQLite database URL (fallback)"""
        return "sqlite:///./data/quantum_commerce.db"