"""
Real Database Models
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Decimal, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid

Base = declarative_base()

class User(Base):
    """User model với real fields"""
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)  # bcrypt hash
    full_name = Column(String(100))
    
    # Status fields
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    
    # Security fields
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime(timezone=True))
    
    # Crypto keys
    dilithium_public_key = Column(Text)  # Public key cho verify signatures
    ibe_identity = Column(String(255))   # IBE identity
    
    # Relationships
    transactions = relationship("Transaction", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")
    
    def __repr__(self):
        return f"<User {self.username} ({self.email})>"

class Transaction(Base):
    """Transaction model với digital signatures"""
    __tablename__ = "transactions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    
    # Transaction data
    amount = Column(Decimal(10, 2), nullable=False)
    currency = Column(String(3), default="USD")
    payment_method = Column(String(50))
    status = Column(String(20), default="pending")  # pending, completed, failed, cancelled
    
    # Quantum-secure signatures
    transaction_data_hash = Column(String(64))  # SHA-256 hash
    dilithium_signature = Column(Text)          # CRYSTALS-Dilithium signature
    signature_algorithm = Column(String(20), default="Dilithium2")
    signature_verified = Column(Boolean, default=False)
    
    # Merchant data
    merchant_id = Column(String(100))
    merchant_public_key = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", back_populates="transactions")
    
    def __repr__(self):
        return f"<Transaction {self.id} - {self.amount} {self.currency}>"

class AuditLog(Base):
    """Audit log cho security events"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(36), ForeignKey("users.id"))
    
    # Event data
    event_type = Column(String(50), nullable=False)  # login, logout, payment, etc.
    event_data = Column(Text)  # JSON data
    ip_address = Column(String(45))  # IPv4/IPv6
    user_agent = Column(Text)
    
    # Security
    session_id = Column(String(36))
    risk_score = Column(Integer, default=0)  # 0-100
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
    
    def __repr__(self):
        return f"<AuditLog {self.event_type} - {self.created_at}>"

class CryptoKey(Base):
    """Crypto keys management"""
    __tablename__ = "crypto_keys"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Key info
    key_type = Column(String(20), nullable=False)  # dilithium, ibe, rsa
    algorithm = Column(String(50))  # Dilithium2, Dilithium3, etc.
    public_key = Column(Text, nullable=False)
    key_usage = Column(String(50))  # signing, encryption, verification
    
    # Ownership
    owner_type = Column(String(20))  # user, merchant, system
    owner_id = Column(String(36))
    
    # Status
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<CryptoKey {self.key_type} - {self.algorithm}>"