"""Mock Dilithium Signer for Testing"""
import uuid
import base64
import json
from datetime import datetime
from typing import Dict, Any, Tuple
from dataclasses import dataclass
from enum import Enum

class SecurityLevel(Enum):
    LEVEL2 = "Dilithium2"
    LEVEL3 = "Dilithium3"
    LEVEL5 = "Dilithium5"

@dataclass
class SignedTransaction:
    transaction_id: str
    timestamp: str
    merchant_id: str
    customer_id: str
    amount: float
    currency: str
    items: list
    signature: str
    algorithm: str
    public_key_id: str

class DilithiumSigner:
    def __init__(self, security_level: SecurityLevel = SecurityLevel.LEVEL2):
        self.security_level = security_level
        self.algorithm = security_level.value
        
    def generate_keypair(self) -> Tuple[bytes, bytes, str]:
        key_id = str(uuid.uuid4())
        public_key = b"mock_dilithium_public_key"
        secret_key = b"mock_dilithium_secret_key"
        return public_key, secret_key, key_id
    
    def sign_transaction(self, transaction_data: Dict[str, Any], secret_key: bytes, key_id: str) -> SignedTransaction:
        return SignedTransaction(
            transaction_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow().isoformat(),
            merchant_id=transaction_data.get("merchant_id", ""),
            customer_id=transaction_data.get("customer_id", ""),
            amount=transaction_data.get("amount", 0),
            currency=transaction_data.get("currency", "USD"),
            items=transaction_data.get("items", []),
            signature=base64.b64encode(b"mock_dilithium_signature").decode(),
            algorithm=self.algorithm,
            public_key_id=key_id
        )

class DilithiumKeyVault:
    def __init__(self, vault_path: str = "./keys/dilithium"):
        self.vault_path = vault_path
        self._keys = {}
        
    def list_active_keys(self) -> Dict[str, Any]:
        if not self._keys:
            # Return default key
            return {
                "default_key_id": {
                    "owner": "merchant@quantumshop.com",
                    "purpose": "transaction_signing",
                    "algorithm": "Dilithium2",
                    "created_at": datetime.utcnow().isoformat(),
                    "status": "active"
                }
            }
        return self._keys
    
    def store_keypair(self, public_key: bytes, secret_key: bytes, key_id: str, owner: str, purpose: str = "transaction_signing"):
        self._keys[key_id] = {
            "owner": owner,
            "purpose": purpose,
            "algorithm": "Dilithium2",
            "created_at": datetime.utcnow().isoformat(),
            "status": "active"
        }
        
    def load_secret_key(self, key_id: str) -> bytes:
        return b"mock_secret_key"
        
    def load_public_key(self, key_id: str) -> bytes:
        return b"mock_public_key"

class TransactionVerifier:
    def __init__(self, key_vault: DilithiumKeyVault):
        self.key_vault = key_vault
        
    def generate_verification_report(self, transaction_json: str) -> Dict[str, Any]:
        return {
            "verification_id": str(uuid.uuid4()),
            "verified_at": datetime.utcnow().isoformat(),
            "transaction_id": json.loads(transaction_json).get("transaction_id", "unknown"),
            "is_valid": True,
            "message": "Transaction signature is valid (mock)",
            "algorithm": "Dilithium2",
            "public_key_id": "default_key_id",
            "verification_details": {
                "signature_length": 2420,
                "timestamp_valid": True,
                "amount_valid": True
            }
        }
