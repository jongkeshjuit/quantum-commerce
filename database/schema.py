"""Database models without ibe_key_data"""
from sqlalchemy import Column, String, DateTime, Numeric, JSON, Boolean, ForeignKey, Text, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = 'users'
    
    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    user_type = Column(String(50), default='customer')
    ibe_key_issued = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    transactions = relationship("Transaction", back_populates="customer")
    audit_logs = relationship("AuditLog", back_populates="user")

class Transaction(Base):
    __tablename__ = 'transactions'
    
    transaction_id = Column(String, primary_key=True, default=generate_uuid)
    payment_id = Column(String, unique=True, nullable=False)
    customer_id = Column(String, ForeignKey('users.id'), nullable=False)
    merchant_id = Column(String, nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), nullable=False)
    payment_method = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False)
    signature = Column(Text)
    public_key_id = Column(String)
    encrypted_data = Column(JSON)
    gateway_response = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    customer = relationship("User", back_populates="transactions")
    receipts = relationship("Receipt", back_populates="transaction")

class Receipt(Base):
    __tablename__ = 'receipts'
    
    receipt_id = Column(String, primary_key=True, default=generate_uuid)
    transaction_id = Column(String, ForeignKey('transactions.transaction_id'), nullable=False)
    encrypted_receipt = Column(JSON, nullable=False)
    recipient_identity = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    transaction = relationship("Transaction", back_populates="receipts")

class CryptoKey(Base):
    __tablename__ = 'crypto_keys'
    
    key_id = Column(String, primary_key=True, default=generate_uuid)
    key_type = Column(String(50), nullable=False)
    owner = Column(String, nullable=False)
    purpose = Column(String(100))
    public_key = Column(Text)
    algorithm = Column(String(50))
    status = Column(String(20), default='active')
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    rotated_from = Column(String)

class AuditLog(Base):
    __tablename__ = 'audit_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey('users.id'))
    action = Column(String(100), nullable=False)
    resource = Column(String(100))
    details = Column(JSON)
    ip_address = Column(String(45))
    user_agent = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    user = relationship("User", back_populates="audit_logs")
