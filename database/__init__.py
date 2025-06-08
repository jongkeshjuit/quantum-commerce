# database/__init__.py
"""Database initialization and configuration"""
import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool, NullPool
from config.database import DatabaseConfig
from config.security import SecurityConfig

logger = logging.getLogger(__name__)

def create_db_engine():
    """Create database engine based on configuration"""
    try:
        # Production: use connection pooling
        if SecurityConfig.APP_ENV == 'production':
            engine = create_engine(
                DatabaseConfig.get_database_url(),
                pool_size=20,
                max_overflow=0,
                pool_pre_ping=True,
                echo=DatabaseConfig.DATABASE_ECHO
            )
        else:
            # Development: simpler pooling
            engine = create_engine(
                DatabaseConfig.get_database_url(),
                poolclass=NullPool,
                pool_pre_ping=True,
                echo=DatabaseConfig.DATABASE_ECHO
            )
        
        # Test connection
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        
        logger.info("✅ Connected to PostgreSQL database")
        return engine
        
    except Exception as e:
        logger.warning(f"⚠️ PostgreSQL connection failed: {e}")
        logger.info("🔄 Falling back to SQLite...")
        
        # Fallback to SQLite
        sqlite_url = DatabaseConfig.get_sqlite_url()
        os.makedirs("data", exist_ok=True)
        
        engine = create_engine(
            sqlite_url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=True
        )
        logger.info("✅ Connected to SQLite database")
        return engine

# Create engine
engine = create_db_engine()

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Session:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Export for imports
__all__ = ['engine', 'get_db', 'SessionLocal']