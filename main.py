"""
Quantum-Secure E-commerce API
Main FastAPI application with secure endpoints
"""

from fastapi import FastAPI, HTTPException, Depends, Security, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime, timedelta
from services.auth_service import auth_service
import os
import json
import jwt
import time
import uvicorn
from database.schema import Base, User
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from database.schema import Transaction, Base

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://qsc_user:secure_password@localhost:5432/quantum_commerce"
)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

from contextlib import asynccontextmanager

from services.payment_service import (
    SecurePaymentProcessor, 
    PaymentRequest as ServicePaymentRequest,
    PaymentMethod,
    PaymentStatus
)
from crypto.ibe_system import IBESystem, IBEKeyManager
from crypto.dilithium_signer import DilithiumSigner, TransactionVerifier, DilithiumKeyVault
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
from monitoring.metrics import (
    track_api_request, 
    api_requests,
    payment_counter,
    active_users,
    system_health
)

# Pydantic models for API
class RegisterRequest(BaseModel):
    email: EmailStr
    name: str
    password: str
    user_type: str = Field(default="customer", pattern="^(customer|merchant|admin)$")
    # user_type: str = Field(default="customer", pattern="^(customer|merchant|admin)$")

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# class PaymentRequest(BaseModel):
#     amount: Decimal = Field(gt=0, le=10000)
#     currency: str = Field(default="USD", pattern="^(USD|EUR|GBP|VND)$")
#     payment_method: str = Field(pattern="^(credit_card|debit_card|cryptocurrency|bank_transfer)$")
#     card_data: Optional[Dict[str, str]] = None
#     billing_address: Optional[Dict[str, str]] = None
#     items: Optional[List[Dict[str, Any]]] = None
    
#     @field_validator('amount')
#     @classmethod
#     def validate_amount(cls, v):
#         if v <= 0:
#             raise ValueError('Amount must be positive')
#         return v
class PaymentRequest(BaseModel):
    amount: Decimal = Field(gt=0, le=100000)  # Tăng limit lên 100k
    currency: str = Field(default="USD", pattern="^(USD|EUR|GBP|VND)$")
    payment_method: str = Field(pattern="^(credit_card|debit_card|cryptocurrency|bank_transfer)$")
    card_data: Optional[Dict[str, str]] = None
    billing_address: Optional[Dict[str, str]] = None
    items: Optional[List[Dict[str, Any]]] = None
    
    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be positive')
        # Convert to Decimal if needed
        return Decimal(str(v))

class TransactionVerifyRequest(BaseModel):
    transaction_id: str
    signature: Optional[str] = None


class RefundRequest(BaseModel):
    transaction_id: str
    amount: Optional[Decimal] = None
    reason: Optional[str] = None


# Response models
class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    ibe_key_issued: bool


class PaymentResponse(BaseModel):
    payment_id: str
    status: str
    transaction_id: Optional[str]
    signature: Optional[str]
    timestamp: Optional[str]
    message: str
    receipt_available: bool = False


# Initialize services
payment_processor = SecurePaymentProcessor()
ibe_system = IBESystem()
ibe_key_manager = IBEKeyManager()
dilithium_signer = DilithiumSigner()
key_vault = DilithiumKeyVault()
verifier = TransactionVerifier(key_vault)

# Security
security = HTTPBearer()
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize app on startup"""
    # Setup crypto systems
    print("Initializing quantum-secure systems...")
    
    # Check if merchant keys exist, if not create them
    active_keys = key_vault.list_active_keys()
    if not active_keys:
        print("Generating merchant signing keys...")
        public_key, secret_key, key_id = dilithium_signer.generate_keypair()
        key_vault.store_keypair(
            public_key, secret_key, key_id, 
            owner="merchant@quantumshop.com",
            purpose="transaction_signing"
        )
    
    print("✓ Quantum-secure e-commerce API ready!")
    yield
    # Cleanup
    print("Shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Quantum-Secure E-Commerce API",
    description="Post-quantum secure payment processing with IBE and Dilithium",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "*"],  # React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Helper functions
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Verify JWT token"""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )


# API Endpoints
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "Quantum-Secure E-Commerce",
        "features": {
            "encryption": "Identity-Based Encryption (IBE)",
            "signatures": "CRYSTALS-Dilithium (Post-Quantum)",
            "security_level": "NIST Level 2"
        }
    }


# @app.post("/api/auth/register", response_model=AuthResponse)
# async def register(request: RegisterRequest):
#     """Register new user and issue IBE key"""
#     try:
#         # In production, check if user exists in database
#         # For demo, create user
        
#         # Generate IBE private key for user
#         master_key = ibe_key_manager.load_master_key(password="secure_master_password")
#         user_ibe_key = ibe_system.extract_user_key(request.email, master_key)
        
#         # Create user record (in production, save to database)
#         user_id = f"user_{request.email.split('@')[0]}_{datetime.utcnow().timestamp()}"
        
#         # Create access token
#         access_token = create_access_token(
#             data={
#                 "sub": user_id,
#                 "email": request.email,
#                 "user_type": request.user_type
#             }
#         )
        
#         return AuthResponse(
#             access_token=access_token,
#             user_id=user_id,
#             email=request.email,
#             ibe_key_issued=True
#         )
        
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=f"Registration failed: {str(e)}"
#         )
# Update endpoint register
@app.post("/api/auth/register", response_model=AuthResponse)
async def register(request: RegisterRequest):
    """Register new user and issue IBE key"""
    try:
        result = await auth_service.register_user(
            email=request.email,
            name=request.name,
            password=request.password,
            user_type=request.user_type
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )



# @app.post("/api/auth/login", response_model=AuthResponse)
# async def login(request: LoginRequest):
#     """Authenticate user"""
#     # In production, verify password hash from database
#     # For demo, accept any valid email format
    
#     user_id = f"user_{request.email.split('@')[0]}"
    
#     # Create access token
#     access_token = create_access_token(
#         data={
#             "sub": user_id,
#             "email": request.email,
#             "user_type": "customer"
#         }
#     )
    
#     return AuthResponse(
#         access_token=access_token,
#         user_id=user_id,
#         email=request.email,
#         ibe_key_issued=True
#     )
# Update endpoint login
@app.post("/api/auth/login", response_model=AuthResponse)
async def login(request: LoginRequest, req: Request):
    """Authenticate user"""
    try:
        # Get client info
        ip_address = req.client.host
        user_agent = req.headers.get("user-agent")
        
        result = await auth_service.login_user(
            email=request.email,
            password=request.password,
            ip_address=ip_address,
            user_agent=user_agent
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )

# @app.post("/api/payments/process", response_model=PaymentResponse)
# async def process_payment(
#     request: PaymentRequest,
#     current_user: dict = Depends(verify_token)
# ):
#     """Process a secure payment"""
#     try:
#         # Convert API request to service request
#         service_request = ServicePaymentRequest(
#             customer_id=current_user["sub"],
#             merchant_id="MERCH001",  # In production, from merchant context
#             amount=request.amount,
#             currency=request.currency,
#             payment_method=PaymentMethod(request.payment_method),
#             card_data=request.card_data,
#             billing_address=request.billing_address,
#             items=request.items
#         )
        
#         # Process payment
#         result = await payment_processor.process_payment(service_request)
        
#         return PaymentResponse(
#             payment_id=result.payment_id,
#             status=result.status.value,
#             transaction_id=result.transaction_id,
#             signature=result.signature,
#             timestamp=result.timestamp,
#             message=result.message or "Payment processed",
#             receipt_available=result.encrypted_receipt is not None
#         )
        
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=f"Payment processing failed: {str(e)}"
#         )
@app.post("/api/payments/process", response_model=PaymentResponse)
async def process_payment(
    request: PaymentRequest,
    current_user: dict = Depends(verify_token)
):
    """Process a secure payment"""
    try:
        # Log request để debug
        print(f"Payment request: amount={request.amount}, method={request.payment_method}")
        
        # Convert API request to service request
        service_request = ServicePaymentRequest(
            customer_id=current_user["sub"],
            merchant_id="MERCH001",
            amount=float(request.amount),  # Convert to float for service
            currency=request.currency,
            payment_method=PaymentMethod(request.payment_method),
            card_data=request.card_data,
            billing_address=request.billing_address,
            items=request.items or []
        )
        
        # Process payment
        result = await payment_processor.process_payment(service_request)
        
        # Save to database
        db = SessionLocal()
        try:
            transaction = Transaction(
                transaction_id=result.transaction_id,
                payment_id=result.payment_id,
                customer_id=current_user["sub"],
                merchant_id="MERCH001",
                amount=request.amount,
                currency=request.currency,
                payment_method=request.payment_method,
                status=result.status.value,
                signature=result.signature,
                created_at=datetime.utcnow()
            )
            db.add(transaction)
            db.commit()
        finally:
            db.close()
        
        return PaymentResponse(
            payment_id=result.payment_id,
            status=result.status.value,
            transaction_id=result.transaction_id,
            signature=result.signature,
            timestamp=result.timestamp,
            message=result.message or "Payment processed successfully",
            receipt_available=result.encrypted_receipt is not None
        )
        
    except Exception as e:
        print(f"Payment error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payment processing failed: {str(e)}"
        )


@app.get("/api/payments/{payment_id}")
async def get_payment_status(
    payment_id: str,
    current_user: dict = Depends(verify_token)
):
    """Get payment status"""
    # In production, fetch from database
    return {
        "payment_id": payment_id,
        "status": "completed",
        "customer_id": current_user["sub"],
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/api/payments/verify")
async def verify_transaction(
    request: TransactionVerifyRequest,
    current_user: dict = Depends(verify_token)
):
    """Verify transaction signature"""
    try:
        # In production, load transaction from database
        # For demo, create mock transaction data
        mock_transaction = {
            "transaction_id": request.transaction_id,
            "timestamp": datetime.utcnow().isoformat(),
            "merchant_id": "MERCH001",
            "customer_id": current_user["sub"],
            "amount": 99.99,
            "currency": "USD",
            "items": [],
            "signature": request.signature or "mock_signature",
            "algorithm": "Dilithium2",
            "public_key_id": list(key_vault.list_active_keys().keys())[0]
        }
        
        # Generate verification report
        report = verifier.generate_verification_report(json.dumps(mock_transaction))
        
        return {
            "verification_id": report["verification_id"],
            "transaction_id": request.transaction_id,
            "is_valid": report["is_valid"],
            "message": report["message"],
            "verified_at": report["verified_at"],
            "details": report["verification_details"]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Verification failed: {str(e)}"
        )


@app.post("/api/payments/refund")
async def refund_payment(
    request: RefundRequest,
    current_user: dict = Depends(verify_token)
):
    """Process payment refund"""
    try:
        result = await payment_processor.refund_payment(
            transaction_id=request.transaction_id,
            amount=request.amount,
            reason=request.reason
        )
        
        return {
            "refund_id": result.payment_id,
            "original_transaction": request.transaction_id,
            "status": result.status.value,
            "message": result.message,
            "timestamp": result.timestamp
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Refund failed: {str(e)}"
        )


# @app.get("/api/transactions")
# async def list_transactions(
#     current_user: dict = Depends(verify_token),
#     limit: int = 10,
#     offset: int = 0
# ):
#     """List user's transactions"""
#     # In production, fetch from database with pagination
#     return {
#         "transactions": [
#             {
#                 "transaction_id": f"TXN00{i}",
#                 "amount": 50.00 + i * 10,
#                 "currency": "USD",
#                 "status": "completed",
#                 "timestamp": (datetime.utcnow() - timedelta(days=i)).isoformat()
#             }
#             for i in range(min(limit, 5))
#         ],
#         "total": 5,
#         "limit": limit,
#         "offset": offset
#     }
@app.get("/api/transactions")
async def list_transactions(
    current_user: dict = Depends(verify_token),
    limit: int = 10,
    offset: int = 0
):
    """List user's transactions"""
    db = SessionLocal()
    try:
        # Lấy transactions thực từ database
        transactions = db.query(Transaction).filter(
            Transaction.customer_id == current_user["sub"]
        ).order_by(
            Transaction.created_at.desc()
        ).offset(offset).limit(limit).all()
        
        # Nếu không có transactions, trả về mock data
        if not transactions:
            return {
                "transactions": [
                    {
                        "transaction_id": f"TXN-DEMO-{i:03d}",
                        "amount": 50.00 + i * 10,
                        "currency": "USD",
                        "status": "completed",
                        "timestamp": (datetime.utcnow() - timedelta(days=i)).isoformat()
                    }
                    for i in range(min(limit, 3))
                ],
                "total": 3,
                "limit": limit,
                "offset": offset
            }
        
        # Format real transactions
        return {
            "transactions": [
                {
                    "transaction_id": tx.transaction_id,
                    "amount": float(tx.amount),
                    "currency": tx.currency,
                    "status": tx.status,
                    "timestamp": tx.created_at.isoformat()
                }
                for tx in transactions
            ],
            "total": db.query(Transaction).filter(
                Transaction.customer_id == current_user["sub"]
            ).count(),
            "limit": limit,
            "offset": offset
        }
    finally:
        db.close()

# Admin endpoints 
@app.get("/api/admin/transactions")
async def get_admin_transactions(
    current_user: dict = Depends(verify_token),
    limit: int = 20
):
    """Get all transactions (admin only)"""
    # Check if user is admin
    if current_user.get("user_type") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    db = SessionLocal()
    try:
        transactions = db.query(Transaction).order_by(
            Transaction.created_at.desc()
        ).limit(limit).all()
        
        return {
            "transactions": [
                {
                    "transaction_id": tx.transaction_id,
                    "amount": float(tx.amount),
                    "currency": tx.currency,
                    "status": tx.status,
                    "timestamp": tx.created_at.isoformat(),
                    "customer_id": tx.customer_id
                }
                for tx in transactions
            ]
        }
    finally:
        db.close()

@app.get("/api/admin/stats")
async def get_admin_stats(
    current_user: dict = Depends(verify_token)
):
    """Get system statistics (admin only)"""
    if current_user.get("user_type") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    db = SessionLocal()
    try:
        total_transactions = db.query(Transaction).count()
        completed_transactions = db.query(Transaction).filter(
            Transaction.status == "completed"
        ).count()
        total_revenue = db.query(func.sum(Transaction.amount)).filter(
            Transaction.status == "completed"
        ).scalar() or 0
        active_users = db.query(User).count()
        
        success_rate = (completed_transactions / total_transactions * 100) if total_transactions > 0 else 0
        
        return {
            "total_transactions": total_transactions,
            "total_revenue": float(total_revenue),
            "active_users": active_users,
            "success_rate": success_rate
        }
    finally:
        db.close()

# Thêm endpoint này vào main.py
@app.get("/metrics")
async def get_metrics():
    """Prometheus metrics endpoint"""
    return Response(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )

# Thêm middleware để track requests
@app.middleware("http")
async def track_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    
    # Track request metrics
    api_requests.labels(
        method=request.method,
        endpoint=request.url.path,
        status_code=response.status_code
    ).inc()
    
    return response

@app.get("/api/crypto/ibe/public-params")
async def get_ibe_public_params():
    """Get IBE public parameters for encryption"""
    try:
        public_params = ibe_key_manager.load_public_params()
        return {
            "status": "success",
            "public_params": public_params
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load public parameters: {str(e)}"
        )


@app.get("/api/crypto/keys/merchant-public")
async def get_merchant_public_keys():
    """Get merchant's public keys for signature verification"""
    try:
        active_keys = key_vault.list_active_keys()
        public_keys = {}
        
        for key_id, metadata in active_keys.items():
            if metadata["purpose"] == "transaction_signing":
                public_key = key_vault.load_public_key(key_id)
                public_keys[key_id] = {
                    "key": public_key.hex(),
                    "algorithm": metadata["algorithm"],
                    "expires_at": metadata["expires_at"]
                }
        
        return {
            "status": "success",
            "public_keys": public_keys
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load public keys: {str(e)}"
        )


@app.post("/api/receipts/decrypt")
async def decrypt_receipt(
    encrypted_receipt: Dict[str, Any],
    current_user: dict = Depends(verify_token)
):
    """Decrypt a payment receipt for the user"""
    try:
        # Load user's IBE key
        master_key = ibe_key_manager.load_master_key(password="secure_master_password")
        user_key = ibe_system.extract_user_key(current_user["email"], master_key)
        
        # Decrypt receipt
        decrypted_data = ibe_system.decrypt(encrypted_receipt, user_key)
        receipt = json.loads(decrypted_data)
        
        return {
            "status": "success",
            "receipt": receipt
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to decrypt receipt: {str(e)}"
        )


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "timestamp": datetime.utcnow().isoformat()
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
# Serve frontend
from fastapi.staticfiles import StaticFiles
app.mount("/", StaticFiles(directory="static", html=True), name="static")
