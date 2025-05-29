"""Mock implementations for testing without full crypto setup"""

import json
import uuid
import base64
from datetime import datetime
from typing import Dict, Any, Tuple

# Mock IBE System
class IBESystem:
    def setup(self):
        return b"mock_master_key", {"public": "mock_public_params"}
    
    def extract_user_key(self, identity: str, master_key: bytes):
        return {
            "identity": identity,
            "private_key": base64.b64encode(b"mock_private_key").decode(),
            "issued_at": datetime.utcnow().isoformat()
        }
    
    def encrypt(self, data: str, identity: str, public_params: Dict):
        return {
            "ciphertext": base64.b64encode(data.encode()).decode(),
            "recipient": identity,
            "encrypted": True
        }
    
    def decrypt(self, encrypted_data: Dict, user_key: Dict):
        return base64.b64decode(encrypted_data["ciphertext"]).decode()

class IBEKeyManager:
    def __init__(self, storage_path="./keys"):
        pass
    
    def save_master_key(self, key: bytes, password: str):
        pass
    
    def load_master_key(self, password: str):
        return b"mock_master_key"
    
    def save_public_params(self, params: Dict):
        pass
    
    def load_public_params(self):
        return {"public": "mock_params"}

# Mock Dilithium
class DilithiumSigner:
    def generate_keypair(self):
        return b"mock_public_key", b"mock_secret_key", str(uuid.uuid4())
    
    def sign_transaction(self, data: Dict, secret_key: bytes, key_id: str):
        from dataclasses import dataclass
        
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
            
        return SignedTransaction(
            transaction_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow().isoformat(),
            merchant_id=data.get("merchant_id", ""),
            customer_id=data.get("customer_id", ""),
            amount=data.get("amount", 0),
            currency=data.get("currency", "USD"),
            items=data.get("items", []),
            signature=base64.b64encode(b"mock_signature").decode(),
            algorithm="MockDilithium",
            public_key_id=key_id
        )

class DilithiumKeyVault:
    def __init__(self, vault_path="./keys/dilithium"):
        self.keys = {
            "mock_key_id": {
                "owner": "merchant@example.com",
                "purpose": "transaction_signing",
                "algorithm": "Dilithium2",
                "status": "active"
            }
        }
    
    def list_active_keys(self):
        return self.keys
    
    def store_keypair(self, public_key, secret_key, key_id, owner, purpose):
        self.keys[key_id] = {
            "owner": owner,
            "purpose": purpose,
            "algorithm": "Dilithium2",
            "status": "active"
        }
    
    def load_secret_key(self, key_id):
        return b"mock_secret_key"
    
    def load_public_key(self, key_id):
        return b"mock_public_key"

class TransactionVerifier:
    def __init__(self, key_vault):
        self.key_vault = key_vault
    
    def generate_verification_report(self, transaction_json: str):
        return {
            "verification_id": str(uuid.uuid4()),
            "verified_at": datetime.utcnow().isoformat(),
            "transaction_id": "mock_tx_id",
            "is_valid": True,
            "message": "Mock verification successful",
            "algorithm": "MockDilithium",
            "public_key_id": "mock_key_id",
            "verification_details": {
                "signature_length": 64,
                "timestamp_valid": True,
                "amount_valid": True
            }
        }