#!/usr/bin/env python3
"""Create database schema"""

import os
from sqlalchemy import create_engine, text

# Database URL
db_url = "postgresql://quantum_user:quantum_pass@localhost:5432/postgres"

# Create engine
engine = create_engine(db_url)

# Create database if not exists
with engine.connect() as conn:
    conn.execute(text("COMMIT"))  # Exit any transaction
    exists = conn.execute(
        text("SELECT 1 FROM pg_database WHERE datname = 'quantum_commerce'")
    ).fetchone()
    
    if not exists:
        conn.execute(text("CREATE DATABASE quantum_commerce"))
        print("✓ Database 'quantum_commerce' created")
    else:
        print("✓ Database 'quantum_commerce' already exists")

print("✓ Database setup completed!")