# crypto/real_dilithium.py
"""
Real Dilithium implementation using pqcrypto
"""
import os
import json
import base64
from typing import Tuple, Dict, Optional
from datetime import datetime
import pqcrypto.sign.dilithium2 as dilithium2
import pqcrypto.sign.dilithium3 as dilithium3
import pqcrypto.sign.dilithium5 as dilithium5
from config.security import SecurityConfig
import logging

logger = logging.getLogger(__name__)

class RealDilithiumSigner:
    """Production-ready Dilithium digital signature implementation"""
    
    # Dilithium variants
    VARIANTS = {
        'dilithium2': dilithium2,  # NIST Level 2
        'dilithium3': dilithium3,  # NIST Level 3 (recommended)
        'dilithium5': dilithium5,  # NIST Level 5 (highest security)
    }
    
    def __init__(self, variant: str = 'dilithium3'):
        """Initialize with specified Dilithium variant"""
        if variant not in self.VARIANTS:
            raise ValueError(f"Invalid variant. Choose from: {list(self.VARIANTS.keys())}")
        
        self.variant = variant
        self.dilithium = self.VARIANTS[variant]
        self.keys_dir = "keys/dilithium"
        os.makedirs(self.keys_dir, exist_ok=True)
        
        # Load or generate master keypair
        self._load_or_generate_master_key()
    
    def _load_or_generate_master_key(self):
        """Load existing master key or generate new one"""
        master_key_path = os.path.join(self.keys_dir, f"master_{self.variant}.json")
        
        try:
            if os.path.exists(master_key_path) and SecurityConfig.APP_ENV != 'development':
                # Load existing key in production
                with open(master_key_path, 'r') as f:
                    key_data = json.load(f)
                    self.master_public_key = base64.b64decode(key_data['public_key'])
                    self.master_secret_key = base64.b64decode(key_data['secret_key'])
                    logger.info(f"Loaded existing {self.variant} master key")
            else:
                # Generate new key
                self.master_public_key, self.master_secret_key = self.generate_keypair()
                
                # Save key (encrypted in production)
                self._save_master_key(master_key_path)
                logger.info(f"Generated new {self.variant} master key")
                
        except Exception as e:
            logger.error(f"Error loading master key: {e}")
            raise
    
    def _save_master_key(self, path: str):
        """Save master key (encrypted in production)"""
        key_data = {
            'variant': self.variant,
            'public_key': base64.b64encode(self.master_public_key).decode(),
            'secret_key': base64.b64encode(self.master_secret_key).decode(),
            'created_at': datetime.utcnow().isoformat(),
        }
        
        if SecurityConfig.APP_ENV == 'production':
            # In production, encrypt before saving
            from cryptography.fernet import Fernet
            f = Fernet(SecurityConfig.get_fernet_key())
            encrypted_data = f.encrypt(json.dumps(key_data).encode())
            
            with open(path, 'wb') as file:
                file.write(encrypted_data)
        else:
            # Development: save as plain JSON
            with open(path, 'w') as f:
                json.dump(key_data, f, indent=2)
    
    def generate_keypair(self) -> Tuple[bytes, bytes]:
        """Generate a new Dilithium keypair"""
        public_key, secret_key = self.dilithium.generate_keypair()
        return public_key, secret_key
    
    def sign(self, message: bytes, secret_key: bytes = None) -> bytes:
        """Sign a message using Dilithium"""
        if secret_key is None:
            secret_key = self.master_secret_key
        
        signature = self.dilithium.sign(secret_key, message)
        return signature
    
    def verify(self, message: bytes, signature: bytes, public_key: bytes = None) -> bool:
        """Verify a Dilithium signature"""
        if public_key is None:
            public_key = self.master_public_key
        
        try:
            self.dilithium.verify(public_key, message, signature)
            return True
        except Exception:
            return False
    
    def sign_transaction(self, transaction_data: Dict) -> Dict:
        """Sign a transaction with Dilithium"""
        # Serialize transaction data
        message = json.dumps(transaction_data, sort_keys=True).encode()
        
        # Generate signature
        signature = self.sign(message)
        
        # Return signed transaction
        return {
            'transaction': transaction_data,
            'signature': base64.b64encode(signature).decode(),
            'public_key': base64.b64encode(self.master_public_key).decode(),
            'algorithm': f'dilithium_{self.variant}',
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
            
            # Verify signature
            return self.verify(message, signature, public_key)
            
        except Exception as e:
            logger.error(f"Transaction verification failed: {e}")
            return False
    
    def get_public_key_info(self) -> Dict:
        """Get public key information"""
        return {
            'algorithm': f'dilithium_{self.variant}',
            'public_key': base64.b64encode(self.master_public_key).decode(),
            'key_size': len(self.master_public_key),
            'security_level': self._get_security_level()
        }
    
    def _get_security_level(self) -> str:
        """Get NIST security level"""
        levels = {
            'dilithium2': 'NIST Level 2 (≈AES-128)',
            'dilithium3': 'NIST Level 3 (≈AES-192)', 
            'dilithium5': 'NIST Level 5 (≈AES-256)'
        }
        return levels.get(self.variant, 'Unknown')