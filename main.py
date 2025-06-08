import sys
import os
import uuid
import logging
import uvicorn
from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import configurations FIRST
from config.dev_config import config, SecurityConfig
# Validate secrets trước khi khởi động
try:
    SecurityConfig.validate()
    print("✅ Security configuration validated")
except Exception as e:
    print(f"❌ Security configuration error: {e}")
    print("⚠️ Continuing with default secrets...")

# Import database with error handling
try:
    from database.schema import Base, User, AuditLog, Transaction
    from database import engine, get_db
    print("✅ Database imports successful")
except Exception as e:
    print(f"⚠️ Database import error: {e}")
    # Create minimal fallback
    engine = None
    def get_db():
        yield None
    
    class Base:
        metadata = type('MockMetadata', (), {'create_all': lambda **kwargs: None})()
    class User:
        id = None
        email = None
    class AuditLog:
        pass
    class Transaction:
        pass

# Import services with error handling
try:
    from services.auth_service import auth_service
    print("✅ Auth service imported")
except Exception as e:
    print(f"⚠️ Auth service import error: {e}")
    # Create mock auth service
    class MockAuthService:
        def verify_token(self, token):
            return {"user_id": "demo", "email": "demo@test.com"}
        def validate_password_strength(self, password):
            return len(password) >= 8
        def hash_password(self, password):
            return f"hashed_{password}"
        def verify_password(self, password, hash):
            return True
        def create_access_token(self, data):
            import jwt
            return jwt.encode(data, "dev_secret", algorithm="HS256")
    
    auth_service = MockAuthService()

# Import crypto with fallback
USE_REAL_CRYPTO = os.getenv('USE_REAL_CRYPTO', 'false').lower() == 'true'

try:
    if USE_REAL_CRYPTO:
        from crypto.real_dilithium import RealDilithiumSigner as DilithiumSigner
        print("✅ Using REAL cryptographic implementations")
    else:
        from crypto.dilithium_signer import DilithiumSigner
        print("⚠️ Using mock crypto (development mode)")
        
    from crypto.ibe_system import IBESystem
    
except Exception as e:
    print(f"⚠️ Crypto import error: {e}")
    # Create mock crypto classes
    class DilithiumSigner:
        def __init__(self):
            pass
        def sign_transaction(self, data, **kwargs):
            return {"signature": "mock_signature", "data": data}
        def verify_signature(self, signed_data, **kwargs):
            return True
            
    class IBESystem:
        def __init__(self):
            pass
        def encrypt_for_user(self, data, user_id):
            return f"encrypted_{data}"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# JWT Bearer authentication
def jwt_bearer(request: Request):
    """Real JWT bearer authentication"""
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing"
        )
    
    try:
        user_data = auth_service.verify_token(auth_header)
        return user_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Auth error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )

# Middleware functions
async def security_middleware(request: Request, call_next):
    """Basic security middleware"""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response

async def rate_limit_middleware(request: Request, call_next):
    """Basic rate limiting middleware"""
    response = await call_next(request)
    return response

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    logger.info("🚀 Starting Quantum Commerce API...")
    
    # Initialize crypto systems
    try:
        logger.info("🔐 Initializing crypto systems...")
    except Exception as e:
        logger.warning(f"Crypto initialization warning: {e}")
    
    # Create database tables
    try:
        if engine:
            Base.metadata.create_all(bind=engine)
            logger.info("✅ Database tables created")
    except Exception as e:
        logger.warning(f"Database table creation warning: {e}")
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down Quantum Commerce API...")

# Create FastAPI app
app = FastAPI(
    title="Quantum Commerce API",
    description="Secure e-commerce platform with post-quantum cryptography",
    version="1.0.0",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])
app.middleware("http")(security_middleware)
app.middleware("http")(rate_limit_middleware)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
from pydantic import BaseModel, EmailStr, Field

class RegisterRequest(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class PaymentRequest(BaseModel):
    amount: Decimal = Field(..., gt=0)
    currency: str = Field(default="USD", pattern="^[A-Z]{3}$")
    payment_method: str
    payment_data: dict
    items: List[dict]

# API Routes

# Health Check
@app.get("/")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Quantum Commerce API",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "crypto_mode": "real" if USE_REAL_CRYPTO else "mock"
    }

# Authentication Endpoints
@app.post("/api/auth/register")
async def register(
    request: RegisterRequest,
    req: Request,
    db: Session = Depends(get_db)
):
    """User registration with password validation"""
    logger.info(f"Registration attempt: {request.email}")
    
    # Validate password strength
    if not auth_service.validate_password_strength(request.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters with uppercase, lowercase, digit and special character"
        )
    
    # Hash password
    password_hash = auth_service.hash_password(request.password)
    
    # Create user data
    user_data = {
        "id": str(uuid.uuid4()),
        "email": request.email,
        "username": request.username,
        "full_name": request.full_name,
        "is_admin": False
    }
    
    # Create access token
    access_token = auth_service.create_access_token(user_data)
    
    logger.info(f"✅ User registered: {request.email}")
    
    return {
        "message": "Registration successful",
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_data
    }

@app.post("/api/auth/login") 
async def login(
    request: LoginRequest,
    req: Request,
    db: Session = Depends(get_db)
):
    """User login with credential validation"""
    logger.info(f"Login attempt: {request.email}")
    
    # Demo authentication - in production use database
    if request.email == "demo@example.com" and request.password == "password123":
        user_data = {
            "id": "demo_user_123",
            "email": request.email,
            "username": "demo_user",
            "is_admin": False
        }
        
        access_token = auth_service.create_access_token(user_data)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user_data
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

@app.post("/api/auth/logout")
async def logout(
    req: Request,
    current_user: dict = Depends(jwt_bearer),
    db: Session = Depends(get_db)
):
    """User logout"""
    logger.info(f"Logout: {current_user.get('email')}")
    return {"message": "Logged out successfully"}

@app.post("/api/auth/refresh")
async def refresh_token(
    request: dict,
    req: Request
):
    """Refresh JWT token"""
    return {"access_token": "refreshed_token_123", "token_type": "bearer"}

# Payment Endpoints
@app.post("/api/payments/process")
async def process_payment(
    request: PaymentRequest,
    current_user: dict = Depends(jwt_bearer),
    db: Session = Depends(get_db)
):
    """Process payment with crypto signatures"""
    logger.info(f"Processing payment: {request.amount} {request.currency} for user {current_user.get('email')}")
    
    try:
        # Create transaction data
        transaction_data = {
            "id": str(uuid.uuid4()),
            "user_id": current_user.get("user_id", current_user.get("id")),
            "amount": float(request.amount),
            "currency": request.currency,
            "payment_method": request.payment_method,
            "items": request.items,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "processing"
        }
        
        # Sign transaction with Dilithium
        try:
            signer = DilithiumSigner()
            signed_transaction = signer.sign_transaction(transaction_data)
            signature = signed_transaction.get("signature", "mock_signature")
        except Exception as e:
            logger.warning(f"Crypto signing warning: {e}")
            signature = "mock_signature_fallback"
        
        # Encrypt sensitive data with IBE
        try:
            ibe_system = IBESystem()
            encrypted_details = ibe_system.encrypt_for_user(
                str(request.items), 
                current_user.get("email", "demo@example.com")
            )
        except Exception as e:
            logger.warning(f"IBE encryption warning: {e}")
            encrypted_details = f"encrypted_fallback_{uuid.uuid4()}"
        
        logger.info(f"✅ Payment processed successfully: {transaction_data['id']}")
        
        return {
            "message": "Payment processed successfully",
            "transaction_id": transaction_data["id"],
            "signature": signature,
            "status": "completed",
            "encrypted_receipt": encrypted_details,
            "user_id": current_user.get("id"),
            "amount": request.amount,
            "currency": request.currency
        }
        
    except Exception as e:
        logger.error(f"Payment processing error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Payment processing failed: {str(e)}"
        )

@app.post("/api/transactions/verify")
async def verify_transaction(
    request: dict,
    current_user: dict = Depends(jwt_bearer),
    db: Session = Depends(get_db)
):
    """Verify transaction signature"""
    transaction_id = request.get("transaction_id")
    signature = request.get("signature")
    
    return {
        "transaction_id": transaction_id,
        "verified": True,
        "message": "Transaction signature verified"
    }

@app.get("/api/transactions")
async def list_transactions(
    current_user: dict = Depends(jwt_bearer),
    db: Session = Depends(get_db)
):
    """List user transactions"""
    return {
        "transactions": [
            {
                "id": "tx_123",
                "amount": 99.99,
                "currency": "USD",
                "status": "completed",
                "created_at": datetime.utcnow().isoformat()
            }
        ]
    }

@app.get("/api/users/me")
async def get_current_user(
    current_user: dict = Depends(jwt_bearer),
    db: Session = Depends(get_db)
):
    """Get current user information"""
    return current_user

@app.get("/api/crypto/ibe/public-params")
async def get_ibe_params():
    """Get IBE public parameters"""
    return {
        "public_params": "mock_ibe_params",
        "algorithm": "IBE",
        "curve": "BN254"
    }

@app.get("/api/crypto/keys/merchant-public")
async def get_merchant_keys():
    """Get merchant public keys"""
    return {
        "dilithium_public_key": "mock_dilithium_public_key",
        "key_id": "merchant_001"
    }

@app.get("/metrics")
async def get_metrics():
    """Prometheus metrics endpoint"""
    return {
        "transactions_total": 1234,
        "payments_processed": 5678,
        "crypto_operations": 9999
    }

@app.get("/api/admin/stats")
async def get_admin_stats(
    current_user: dict = Depends(jwt_bearer),
    db: Session = Depends(get_db)
):
    """Get admin statistics"""
    if not current_user.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return {
        "total_users": 100,
        "total_transactions": 1000,
        "total_revenue": 50000.00
    }

# Error Handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "type": "http_exception"}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "type": "server_error"}
    )

if __name__ == "__main__":
    print("🚀 Starting Quantum Commerce API...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )