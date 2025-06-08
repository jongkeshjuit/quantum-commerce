# crypto/real_dilithium_liboqs.py
"""
Real Dilithium implementation using liboqs
"""
import os
import json
import base64
from typing import Tuple, Dict, Optional
from datetime import datetime
import oqs  # from liboqs-python
from config.dev_config import SecurityConfig
import logging

logger = logging.getLogger(__name__)

class RealDilithiumSigner:
    """Production-ready Dilithium using liboqs"""
    
    def __init__(self, variant: str = 'Dilithium3'):
        """Initialize with specified Dilithium variant"""
        self.variant = variant
        self.algorithm = f"dilithium_{variant.lower()}"
        
        # Initialize OQS signature object
        self.sig = oqs.Signature(variant)
        
        # Generate or load keys
        self._load_or_generate_keys()
        
        logger.info(f"Initialized Real Dilithium Signer with {variant}")
    
    def _load_or_generate_keys(self):
        """Load or generate keypair"""
        keys_dir = "keys/dilithium"
        os.makedirs(keys_dir, exist_ok=True)
        
        key_file = os.path.join(keys_dir, f"{self.variant}_keys.json")
        
        if os.path.exists(key_file):
            # Load existing keys
            with open(key_file, 'r') as f:
                key_data = json.load(f)
                self.public_key = base64.b64decode(key_data['public_key'])
                self.secret_key = base64.b64decode(key_data['secret_key'])
            logger.info("Loaded existing Dilithium keys")
        else:
            # Generate new keys
            self.public_key = self.sig.generate_keypair()
            self.secret_key = self.sig.export_secret_key()
            
            # Save keys
            key_data = {
                'variant': self.variant,
                'public_key': base64.b64encode(self.public_key).decode(),
                'secret_key': base64.b64encode(self.secret_key).decode(),
                'created_at': datetime.utcnow().isoformat()
            }
            
            with open(key_file, 'w') as f:
                json.dump(key_data, f, indent=2)
            logger.info("Generated new Dilithium keypair")
    
    def generate_keypair(self) -> Tuple[bytes, bytes]:
        """Generate a new Dilithium keypair"""
        sig = oqs.Signature(self.variant)
        public_key = sig.generate_keypair()
        secret_key = sig.export_secret_key()
        return public_key, secret_key
    
    def sign(self, message: bytes) -> bytes:
        """Sign a message"""
        signature = self.sig.sign(message)
        return signature
    
    def verify(self, message: bytes, signature: bytes, public_key: bytes = None) -> bool:
        """Verify a signature"""
        if public_key is None:
            public_key = self.public_key
            
        verifier = oqs.Signature(self.variant)
        is_valid = verifier.verify(message, signature, public_key)
        return is_valid
    
    def sign_transaction(self, transaction_data: Dict) -> Dict:
        """Sign a transaction - matches mock interface"""
        # Serialize transaction
        message = json.dumps(transaction_data, sort_keys=True).encode()
        
        # Generate signature
        signature = self.sign(message)
        
        # Return signed transaction
        return {
            'transaction': transaction_data,
            'signature': base64.b64encode(signature).decode(),
            'public_key': base64.b64encode(self.public_key).decode(),
            'algorithm': self.algorithm,
            'signed_at': datetime.utcnow().isoformat()
        }
    
    def verify_transaction(self, signed_transaction: Dict) -> bool:
        """Verify a signed transaction"""
        try:
            # Extract components
            transaction_data = signed_transaction['transaction']
            signature = base64.b64decode(signed_transaction['signature'])
            public_key = base64.b64decode(signed_transaction['public_key'])
            
            # Recreate message
            message = json.dumps(transaction_data, sort_keys=True).encode()
            
            # Verify
            return self.verify(message, signature, public_key)
            
        except Exception as e:
            logger.error(f"Verification failed: {e}")
            return False