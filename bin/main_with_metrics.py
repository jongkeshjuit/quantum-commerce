# main_with_metrics.py
"""
Quantum-Secure E-Commerce API với Prometheus Metrics
"""
import os
import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Response
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

# Import metrics
from metrics.quantum_metrics import (
    track_quantum_signature, track_quantum_verification, 
    track_ibe_encryption, track_api_request, get_metrics,
    payments_total, payment_amount, security_events_total
)

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
    logger.info("🚀 Starting Quantum-Secure E-Commerce API with Metrics")
    
    if crypto_instances:
        logger.info("✅ Crypto system initialized")
        # Log security event
        security_events_total.labels(event_type='startup', severity='info').inc()
    else:
        logger.warning("⚠️ Crypto system not available")
        security_events_total.labels(event_type='crypto_failure', severity='warning').inc()
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down API")
    security_events_total.labels(event_type='shutdown', severity='info').inc()

# Create FastAPI app
app = FastAPI(
    title="Quantum-Secure E-Commerce API",
    description="E-commerce API with post-quantum cryptography and metrics",
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
@track_api_request("GET", "/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Quantum-Secure E-Commerce API",
        "status": "healthy",
        "crypto_ready": crypto_instances is not None,
        "quantum_secure": crypto_status.get('quantum_secure_signatures', False) if crypto_instances else False,
        "metrics_enabled": True
    }

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(get_metrics(), media_type="text/plain")

@app.get("/api/crypto/status")
@track_api_request("GET", "/api/crypto/status")
async def crypto_status_endpoint():
    """Get crypto system status"""
    if not crypto_instances:
        raise HTTPException(status_code=503, detail="Crypto system not available")
    
    return {
        "status": "active",
        "capabilities": crypto_status,
        "signer": {
            "algorithm": crypto_instances['signer'].variant,
            "quantum_secure": hasattr(crypto_instances['signer'], 'signer') and crypto_instances['signer'].signer is not None,
            "security_level": crypto_instances['signer']._get_security_level()
        },
        "ibe": {
            "algorithm": "enhanced_ibe_aes_gcm",
            "encryption": "AES-256-GCM"
        },
        "metrics": "enabled"
    }

@app.post("/api/crypto/sign")
@track_api_request("POST", "/api/crypto/sign")
async def sign_transaction(transaction_data: dict):
    """Sign transaction với quantum-secure Dilithium + metrics"""
    if not crypto_instances:
        raise HTTPException(status_code=503, detail="Crypto system not available")
    
    try:
        # Apply metrics decorator to the signing function
        @track_quantum_signature(crypto_instances['signer'].variant)
        def do_signing():
            return crypto_instances['signer'].sign_transaction(transaction_data)
        
        signed = do_signing()
        
        logger.info(f"✅ Transaction signed: {signed.get('algorithm')}")
        
        return {
            "status": "success",
            "signed_transaction": signed,
            "quantum_secure": signed.get('quantum_secure', False),
            "algorithm": signed.get('algorithm'),
            "security_level": signed.get('security_level'),
            "metrics_tracked": True
        }
        
    except Exception as e:
        logger.error(f"Signing failed: {e}")
        security_events_total.labels(event_type='signing_failure', severity='error').inc()
        raise HTTPException(status_code=500, detail=f"Signing failed: {str(e)}")

@app.post("/api/crypto/verify")
@track_api_request("POST", "/api/crypto/verify")
async def verify_signature(signed_data: dict):
    """Verify quantum-secure signature + metrics"""
    if not crypto_instances:
        raise HTTPException(status_code=503, detail="Crypto system not available")
    
    try:
        # Apply metrics decorator to verification
        @track_quantum_verification(signed_data.get('algorithm', 'unknown'))
        def do_verification():
            return crypto_instances['signer'].verify_signature(signed_data)
        
        verified = do_verification()
        
        logger.info(f"✅ Signature verified: {verified}")
        
        return {
            "status": "success",
            "verified": verified,
            "algorithm": signed_data.get('algorithm'),
            "quantum_secure": signed_data.get('quantum_secure', False),
            "metrics_tracked": True
        }
        
    except Exception as e:
        logger.error(f"Verification failed: {e}")
        security_events_total.labels(event_type='verification_failure', severity='error').inc()
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")

@app.post("/api/crypto/encrypt")
@track_api_request("POST", "/api/crypto/encrypt")
async def encrypt_data(data: dict):
    """Encrypt data cho user với IBE + metrics"""
    if not crypto_instances:
        raise HTTPException(status_code=503, detail="Crypto system not available")
    
    message = data.get('message', '')
    identity = data.get('identity', '')
    
    if not message or not identity:
        raise HTTPException(status_code=400, detail="Message and identity required")
    
    try:
        # Apply metrics decorator to IBE encryption
        @track_ibe_encryption("enhanced_ibe_aes_gcm")
        def do_encryption():
            return crypto_instances['ibe'].encrypt_for_user(message, identity)
        
        encrypted = do_encryption()
        
        logger.info(f"✅ Data encrypted for: {identity}")
        
        return {
            "status": "success",
            "encrypted_data": encrypted,
            "algorithm": encrypted.get('algorithm'),
            "metrics_tracked": True
        }
        
    except Exception as e:
        logger.error(f"Encryption failed: {e}")
        security_events_total.labels(event_type='encryption_failure', severity='error').inc()
        raise HTTPException(status_code=500, detail=f"Encryption failed: {str(e)}")

@app.post("/api/payments/process")
@track_api_request("POST", "/api/payments/process")
async def process_payment(payment_data: dict):
    """Process payment với metrics"""
    
    amount = payment_data.get('amount', 0)
    currency = payment_data.get('currency', 'USD')
    
    try:
        # Simulate payment processing
        if amount <= 0:
            raise ValueError("Invalid amount")
        
        # Record payment metrics
        payments_total.labels(status='success', currency=currency).inc()
        payment_amount.observe(amount)
        
        # Sign the payment transaction
        transaction = {
            "transaction_id": f"pay_{hash(str(payment_data))}",
            "amount": amount,
            "currency": currency,
            "timestamp": "2025-01-27T00:00:00Z"
        }
        
        if crypto_instances:
            @track_quantum_signature(crypto_instances['signer'].variant)
            def sign_payment():
                return crypto_instances['signer'].sign_transaction(transaction)
            
            signed = sign_payment()
            
            return {
                "status": "success",
                "payment_id": transaction["transaction_id"],
                "amount": amount,
                "currency": currency,
                "signature": signed.get('signature', '')[:50] + "...",
                "quantum_secure": True,
                "metrics_tracked": True
            }
        else:
            return {
                "status": "success",
                "payment_id": transaction["transaction_id"],
                "amount": amount,
                "currency": currency,
                "quantum_secure": False,
                "metrics_tracked": True
            }
            
    except Exception as e:
        payments_total.labels(status='failed', currency=currency).inc()
        security_events_total.labels(event_type='payment_failure', severity='error').inc()
        raise HTTPException(status_code=500, detail=f"Payment failed: {str(e)}")

@app.get("/api/health")
@track_api_request("GET", "/api/health")
async def health_check():
    """Detailed health check với metrics info"""
    return {
        "api": "healthy",
        "crypto": crypto_instances is not None,
        "quantum_ready": crypto_status.get('quantum_secure_signatures', False) if crypto_instances else False,
        "metrics": "enabled",
        "prometheus": "http://localhost:9090",
        "grafana": "http://localhost:3030",
        "timestamp": "2025-01-27T00:00:00Z"
    }

@app.get("/api/metrics/summary")
@track_api_request("GET", "/api/metrics/summary")
async def metrics_summary():
    """Summary của metrics cho dashboard"""
    return {
        "crypto_operations": {
            "signatures_enabled": crypto_instances is not None,
            "algorithm": crypto_instances['signer'].variant if crypto_instances else "none",
            "quantum_secure": crypto_status.get('quantum_secure_signatures', False)
        },
        "monitoring": {
            "prometheus": "http://localhost:9090",
            "grafana": "http://localhost:3030",
            "metrics_endpoint": "/metrics"
        },
        "endpoints": {
            "sign": "/api/crypto/sign",
            "verify": "/api/crypto/verify", 
            "encrypt": "/api/crypto/encrypt",
            "payments": "/api/payments/process"
        }
    }

if __name__ == "__main__":
    # Install prometheus client if not installed
    try:
        import prometheus_client
    except ImportError:
        print("Installing prometheus_client...")
        os.system("pip install prometheus-client")
        import prometheus_client
    
    # Run with uvicorn
    uvicorn.run(
        "main_with_metrics:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )