#!/usr/bin/env python3
"""Create database tables"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from database.schema import Base

# FIXED: Sử dụng password đúng từ .env
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://quantum_user:quantum_secure_pass_123@localhost:5432/quantum_commerce"
)

def create_tables():
    """Create all tables"""
    engine = create_engine(DATABASE_URL)
    
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created successfully!")
    
    # List created tables
    print("\nCreated tables:")
    for table in Base.metadata.tables:
        print(f"  - {table}")

if __name__ == "__main__":
    create_tables()