"""Simplified Auth Service"""
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import jwt

from database.schema import User, AuditLog

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://qsc_user:secure_password@postgres:5432/quantum_commerce"
)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440

class AuthService:
    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    async def register_user(self, email: str, name: str, password: str, user_type: str = "customer") -> Dict[str, Any]:
        db = SessionLocal()
        try:
            # Check existing
            existing = db.query(User).filter(User.email == email).first()
            if existing:
                raise ValueError("User already exists")
            
            # Create user
            user = User(
                email=email,
                name=name,
                password_hash=self.hash_password(password),
                user_type=user_type,
                ibe_key_issued=True  # Mock
            )
            
            db.add(user)
            db.commit()
            db.refresh(user)
            
            # Create token
            access_token = self.create_access_token(
                data={
                    "sub": user.id,
                    "email": user.email,
                    "user_type": user.user_type
                }
            )
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user_id": user.id,
                "email": user.email,
                "ibe_key_issued": True
            }
        finally:
            db.close()
    
    async def login_user(self, email: str, password: str, ip_address: str = None, user_agent: str = None) -> Dict[str, Any]:
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.email == email).first()
            if not user or not self.verify_password(password, user.password_hash):
                raise ValueError("Invalid credentials")
            
            access_token = self.create_access_token(
                data={
                    "sub": user.id,
                    "email": user.email,
                    "user_type": user.user_type
                }
            )
            
            # Log
            audit = AuditLog(
                user_id=user.id,
                action="login",
                ip_address=ip_address,
                user_agent=user_agent
            )
            db.add(audit)
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

auth_service = AuthService()
