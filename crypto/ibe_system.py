"""Mock IBE System for Testing"""
import json
import uuid
import base64
from datetime import datetime
from typing import Dict, Any, Tuple
from config.dev_config import SecurityConfig

class IBESystem:
    def __init__(self):
        # Use from config
        self.master_secret = SecurityConfig.IBE_MASTER_KEY
    def setup(self) -> Tuple[bytes, Dict[str, Any]]:
        return b"mock_master_key", {
            "curve": "secp256r1",
            "master_public": "mock_public_key_base64",
            "created_at": datetime.utcnow().isoformat(),
            "version": "1.0"
        }
    
    def extract_user_key(self, identity: str, master_key: bytes) -> Dict[str, Any]:
        return {
            "identity": identity,
            "private_key": base64.b64encode(b"mock_private_key").decode(),
            "issued_at": datetime.utcnow().isoformat(),
            "expires_at": "2025-12-31T23:59:59",
            "algorithm": "ibe-secp256r1-aes256"
        }
    
    def encrypt(self, data: str, identity: str, public_params: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "recipient": identity,
            "ciphertext": base64.b64encode(data.encode()).decode(),
            "iv": base64.b64encode(b"mock_iv_16_bytes").decode(),
            "tag": base64.b64encode(b"mock_tag").decode(),
            "ephemeral_public": "mock_ephemeral_public_key",
            "timestamp": datetime.utcnow().isoformat(),
            "algorithm": "ibe-secp256r1-aes256-gcm"
        }
    
    def decrypt(self, encrypted_data: Dict[str, Any], user_key: Dict[str, Any]) -> str:
        # Mock decrypt - just decode base64
        return base64.b64decode(encrypted_data["ciphertext"]).decode()

class IBEKeyManager:
    def __init__(self, storage_path: str = "./keys"):
        self.storage_path = storage_path
        
    def save_master_key(self, key: bytes, password: str):
        print(f"Mock: Saving master key")
        
    def load_master_key(self, password: str) -> bytes:
        return b"mock_master_key"
        
    def save_public_params(self, params: Dict[str, Any]):
        print(f"Mock: Saving public params")
        
    def load_public_params(self) -> Dict[str, Any]:
        return {
            "curve": "secp256r1", 
            "master_public": "mock_public_key_base64",
            "created_at": "2024-01-01T00:00:00",
            "version": "1.0"
        }
