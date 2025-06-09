#!/usr/bin/env python3
"""Create database tables - FIXED VERSION"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from database.schema import Base

# Load environment variables
load_dotenv()

# Get DATABASE_URL from .env
DATABASE_URL = os.getenv("DATABASE_URL")
print(f"📍 Using DATABASE_URL: {DATABASE_URL}")

def create_tables():
    """Create all tables"""
    try:
        engine = create_engine(DATABASE_URL)
        
        # Test connection first
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection successful!")
        
        print("Creating tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Tables created successfully!")
        
        # List created tables
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            tables = result.fetchall()
            
        print("\n📋 Created tables:")
        for table in tables:
            print(f"   ✓ {table[0]}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        raise

if __name__ == "__main__":
    create_tables()
