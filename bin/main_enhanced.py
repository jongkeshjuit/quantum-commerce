"""
Quantum-Secure E-Commerce API
Enhanced with real crypto
"""
import os
import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import crypto system
try:
    from crypto import get_crypto_status, create_production_crypto
    crypto_status = get_crypto_status()
    crypto_instances = create_production_crypto()
    
    logger.info("🛡️ Crypto System Status:")
    logger.info(f"   Quantum-secure signatures: {crypto_status['quantum_secure_signatures']}")
    logger.info(f"   Enhanced IBE: {crypto_status['enhanced_ibe']}")
    logger.info(f"   Production ready: {crypto_status['production_ready']}")
    
except Exception as e:
    logger.error(f"❌ Crypto system failed: {e}")
    crypto_instances = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Starting Quantum-Secure E-Commerce API")
    
    if crypto_instances:
        logger.info("✅ Crypto system initialized")
    else:
        logger.warning("⚠️ Crypto system not available")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down API")

# Create FastAPI app
app = FastAPI(
    title="Quantum-Secure E-Commerce API",
    description="E-commerce API with post-quantum cryptography",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Quantum-Secure E-Commerce API",
        "status": "healthy",
        "crypto_ready": crypto_instances is not None,
        "quantum_secure": crypto_status.get('quantum_secure_signatures', False) if crypto_instances else False
    }

@app.get("/api/crypto/status")
async def crypto_status_endpoint():
    """Get crypto system status"""
    if not crypto_instances:
        raise HTTPException(status_code=503, detail="Crypto system not available")
    
    return {
        "status": "active",
        "capabilities": crypto_status,
        "signer": {
            "algorithm": crypto_instances['signer'].variant,
            "quantum_secure": getattr(crypto_instances['signer'], 'REAL_DILITHIUM', False),
            "security_level": crypto_instances['signer']._get_security_level()
        },
        "ibe": {
            "algorithm": "enhanced_ibe_aes_gcm",
            "encryption": "AES-256-GCM"
        }
    }

@app.post("/api/crypto/sign")
async def sign_transaction(transaction_data: dict):
    """Sign transaction với quantum-secure Dilithium"""
    if not crypto_instances:
        raise HTTPException(status_code=503, detail="Crypto system not available")
    
    try:
        signed = crypto_instances['signer'].sign_transaction(transaction_data)
        
        return {
            "status": "success",
            "signed_transaction": signed,
            "quantum_secure": signed.get('quantum_secure', False),
            "algorithm": signed.get('algorithm'),
            "security_level": signed.get('security_level')
        }
        
    except Exception as e:
        logger.error(f"Signing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Signing failed: {str(e)}")

@app.post("/api/crypto/verify")
async def verify_signature(signed_data: dict):
    """Verify quantum-secure signature"""
    if not crypto_instances:
        raise HTTPException(status_code=503, detail="Crypto system not available")
    
    try:
        verified = crypto_instances['signer'].verify_signature(signed_data)
        
        return {
            "status": "success",
            "verified": verified,
            "algorithm": signed_data.get('algorithm'),
            "quantum_secure": signed_data.get('quantum_secure', False)
        }
        
    except Exception as e:
        logger.error(f"Verification failed: {e}")
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")

@app.post("/api/crypto/encrypt")
async def encrypt_data(data: dict):
    """Encrypt data cho user với IBE"""
    if not crypto_instances:
        raise HTTPException(status_code=503, detail="Crypto system not available")
    
    message = data.get('message', '')
    identity = data.get('identity', '')
    
    if not message or not identity:
        raise HTTPException(status_code=400, detail="Message and identity required")
    
    try:
        encrypted = crypto_instances['ibe'].encrypt_for_user(message, identity)
        
        return {
            "status": "success",
            "encrypted_data": encrypted,
            "algorithm": encrypted.get('algorithm')
        }
        
    except Exception as e:
        logger.error(f"Encryption failed: {e}")
        raise HTTPException(status_code=500, detail=f"Encryption failed: {str(e)}")

@app.get("/api/health")
async def health_check():
    """Detailed health check"""
    return {
        "api": "healthy",
        "crypto": crypto_instances is not None,
        "quantum_ready": crypto_status.get('quantum_secure_signatures', False) if crypto_instances else False,
        "database": "connected",  # Add actual DB check later
        "timestamp": "2025-01-27T00:00:00Z"
    }

if __name__ == "__main__":
    # Run with uvicorn
    uvicorn.run(
        "main_enhanced:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
