#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from database.schema import Base

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://qsc_user:secure_password@localhost:5432/quantum_commerce"
)

engine = create_engine(DATABASE_URL)

print("Dropping all tables...")
with engine.connect() as conn:
    conn.execute(text("DROP TABLE IF EXISTS audit_logs CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS receipts CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS transactions CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS crypto_keys CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS users CASCADE"))
    conn.commit()
    print("✓ Tables dropped")

print("Creating new tables...")
Base.metadata.create_all(bind=engine)
print("✓ Tables created successfully!")

# List tables
with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT tablename FROM pg_tables 
        WHERE schemaname = 'public'
    """))
    print("\nCreated tables:")
    for row in result:
        print(f"  - {row[0]}")
