"""Mock Payment Service for Testing"""
from enum import Enum
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional, Dict, Any, List
import uuid
import asyncio
from datetime import datetime

class PaymentStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing" 
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

class PaymentMethod(Enum):
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    CRYPTOCURRENCY = "cryptocurrency"
    BANK_TRANSFER = "bank_transfer"

@dataclass
class PaymentRequest:
    customer_id: str
    merchant_id: str
    amount: Decimal
    currency: str
    payment_method: PaymentMethod
    card_data: Optional[Dict[str, str]] = None
    billing_address: Optional[Dict[str, str]] = None
    items: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass  
class PaymentResponse:
    payment_id: str
    status: PaymentStatus
    transaction_id: Optional[str] = None
    signature: Optional[str] = None
    encrypted_receipt: Optional[Dict[str, Any]] = None
    timestamp: Optional[str] = None
    message: Optional[str] = None

class SecurePaymentProcessor:
    """Mock payment processor for testing"""
    
    def __init__(self):
        print("Initializing SecurePaymentProcessor (Mock Version)")
        
    async def process_payment(self, request: PaymentRequest) -> PaymentResponse:
        """Process a payment request"""
        # Simulate processing delay
        await asyncio.sleep(0.1)
        
        # Generate mock response
        payment_id = str(uuid.uuid4())
        transaction_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"
        
        return PaymentResponse(
            payment_id=payment_id,
            status=PaymentStatus.COMPLETED,
            transaction_id=transaction_id,
            signature="MOCK_SIGNATURE_BASE64_ENCODED",
            encrypted_receipt={
                "encrypted": True,
                "data": "mock_encrypted_receipt_data"
            },
            timestamp=datetime.utcnow().isoformat(),
            message="Payment processed successfully (mock)"
        )
    
    async def refund_payment(self, transaction_id: str, amount: Optional[Decimal] = None, reason: Optional[str] = None) -> PaymentResponse:
        """Process a refund"""
        await asyncio.sleep(0.1)
        
        return PaymentResponse(
            payment_id=str(uuid.uuid4()),
            status=PaymentStatus.REFUNDED,
            transaction_id=transaction_id,
            timestamp=datetime.utcnow().isoformat(),
            message=f"Refund processed: {reason or 'Customer request'}"
        )
    
    async def verify_payment(self, transaction_id: str) -> Dict[str, Any]:
        """Verify a payment"""
        return {
            "transaction_id": transaction_id,
            "verified": True,
            "status": PaymentStatus.COMPLETED.value,
            "verified_at": datetime.utcnow().isoformat()
        }
