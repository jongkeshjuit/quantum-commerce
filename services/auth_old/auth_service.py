"""
Authentication Service with Database Integration
"""

import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import jwt

from database.schema import User, AuditLog
from crypto.ibe_system import IBESystem, IBEKeyManager

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Database setup
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://qsc_user:secure_password@localhost:5432/quantum_commerce"
)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# JWT settings
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

class AuthService:
    def __init__(self):
        self.ibe_system = IBESystem()
        self.ibe_key_manager = IBEKeyManager()
        
    def get_db(self) -> Session:
        """Get database session"""
        db = SessionLocal()
        try:
            return db
        finally:
            db.close()
            
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def decode_token(self, token: str) -> Dict[str, Any]:
        """Decode JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.JWTError:
            raise ValueError("Invalid token")
    
    async def register_user(self, email: str, name: str, password: str, user_type: str = "customer") -> Dict[str, Any]:
        """Register new user"""
        db = SessionLocal()
        try:
            # Check if user exists
            existing_user = db.query(User).filter(User.email == email).first()
            if existing_user:
                raise ValueError("User already exists")
            
            # Generate IBE key for user
            try:
                master_key = self.ibe_key_manager.load_master_key(password="secure_master_password")
                user_ibe_key = self.ibe_system.extract_user_key(email, master_key)
                ibe_key_issued = True
            except Exception as e:
                print(f"IBE key generation failed: {e}")
                user_ibe_key = None
                ibe_key_issued = False
            
            # Create user
            user = User(
                email=email,
                name=name,
                password_hash=self.hash_password(password),
                user_type=user_type,
                ibe_key_issued=ibe_key_issued,
                ibe_key_data=user_ibe_key
            )
            
            db.add(user)
            db.commit()
            db.refresh(user)
            
            # Create access token
            access_token = self.create_access_token(
                data={
                    "sub": user.id,
                    "email": user.email,
                    "user_type": user.user_type
                }
            )
            
            # Log registration
            audit_log = AuditLog(
                user_id=user.id,
                action="user_registered",
                resource="auth",
                details={"email": email, "user_type": user_type}
            )
            db.add(audit_log)
            db.commit()
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user_id": user.id,
                "email": user.email,
                "ibe_key_issued": ibe_key_issued
            }
            
        finally:
            db.close()
    
    async def login_user(self, email: str, password: str, ip_address: str = None, user_agent: str = None) -> Dict[str, Any]:
        """Authenticate user"""
        db = SessionLocal()
        try:
            # Find user
            user = db.query(User).filter(User.email == email).first()
            if not user:
                raise ValueError("Invalid credentials")
            
            # Verify password
            if not self.verify_password(password, user.password_hash):
                raise ValueError("Invalid credentials")
            
            # Create access token
            access_token = self.create_access_token(
                data={
                    "sub": user.id,
                    "email": user.email,
                    "user_type": user.user_type
                }
            )
            
            # Log login
            audit_log = AuditLog(
                user_id=user.id,
                action="user_login",
                resource="auth",
                ip_address=ip_address,
                user_agent=user_agent,
                details={"email": email}
            )
            db.add(audit_log)
            db.commit()
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user_id": user.id,
                "email": user.email,
                "ibe_key_issued": user.ibe_key_issued
            }
            
        finally:
            db.close()
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        db = SessionLocal()
        try:
            return db.query(User).filter(User.id == user_id).first()
        finally:
            db.close()
    
    def get_user_ibe_key(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user's IBE key"""
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if user and user.ibe_key_data:
                return user.ibe_key_data
            return None
        finally:
            db.close()

# Singleton instance
auth_service = AuthService()