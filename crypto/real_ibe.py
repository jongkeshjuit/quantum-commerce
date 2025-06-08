# crypto/real_ibe.py
"""
Real IBE (Identity-Based Encryption) implementation
Note: This uses a simplified IBE scheme. For production, use established libraries.
"""
import os
import json
import base64
import hashlib
from typing import Dict, Tuple, Optional
from datetime import datetime
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from config.security import SecurityConfig
import logging

logger = logging.getLogger(__name__)

class RealIBESystem:
    """
    Simplified IBE implementation using RSA as base
    For production, use proper IBE libraries like Charm-Crypto
    """
    
    def __init__(self):
        self.backend = default_backend()
        self.keys_dir = "keys/ibe"
        os.makedirs(self.keys_dir, exist_ok=True)
        
        # Load or generate master key
        self._load_or_generate_master_key()
    
    def _load_or_generate_master_key(self):
        """Load or generate IBE master key"""
        master_key_path = os.path.join(self.keys_dir, "master_key.pem")
        
        try:
            if os.path.exists(master_key_path) and SecurityConfig.APP_ENV != 'development':
                # Load existing key
                with open(master_key_path, 'rb') as f:
                    if SecurityConfig.APP_ENV == 'production':
                        # Decrypt the key first
                        from cryptography.fernet import Fernet
                        fernet = Fernet(SecurityConfig.get_fernet_key())
                        key_data = fernet.decrypt(f.read())
                    else:
                        key_data = f.read()
                    
                    self.master_key = serialization.load_pem_private_key(
                        key_data,
                        password=None,
                        backend=self.backend
                    )
                logger.info("Loaded existing IBE master key")
            else:
                # Generate new master key
                self.master_key = rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=4096,  # High security for master key
                    backend=self.backend
                )
                
                # Save the key
                self._save_master_key(master_key_path)
                logger.info("Generated new IBE master key")
                
        except Exception as e:
            logger.error(f"Error with IBE master key: {e}")
            raise
    
    def _save_master_key(self, path: str):
        """Save master key (encrypted in production)"""
        # Serialize private key
        pem = self.master_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        if SecurityConfig.APP_ENV == 'production':
            # Encrypt before saving
            from cryptography.fernet import Fernet
            fernet = Fernet(SecurityConfig.get_fernet_key())
            encrypted_pem = fernet.encrypt(pem)
            
            with open(path, 'wb') as f:
                f.write(encrypted_pem)
        else:
            # Development: save unencrypted
            with open(path, 'wb') as f:
                f.write(pem)
    
    def setup(self) -> Dict:
        """Generate IBE public parameters"""
        public_key = self.master_key.public_key()
        
        # Serialize public key
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        # Generate system parameters
        params = {
            'algorithm': 'simplified-ibe-rsa',
            'master_public_key': base64.b64encode(public_pem).decode(),
            'security_level': '256-bit',
            'key_size': 4096,
            'generated_at': datetime.utcnow().isoformat()
        }
        
        # Save parameters
        params_path = os.path.join(self.keys_dir, "public_params.json")
        with open(params_path, 'w') as f:
            json.dump(params, f, indent=2)
        
        return params
    
    def extract_key(self, identity: str) -> bytes:
        """Extract private key for an identity"""
        # Hash the identity to create deterministic key material
        identity_hash = hashlib.sha256(identity.encode()).digest()
        
        # Use HKDF to derive a key from master secret and identity
        from cryptography.hazmat.primitives.kdf.hkdf import HKDF
        
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,  # 256-bit key
            salt=b'quantum-commerce-ibe',
            info=identity.encode(),
            backend=self.backend
        )
        
        # Derive key material from master key
        master_key_bytes = self.master_key.private_numbers().d.to_bytes(512, 'big')
        identity_key = hkdf.derive(master_key_bytes[:32] + identity_hash)
        
        return identity_key
    
    def encrypt(self, message: bytes, identity: str) -> Dict:
        """Encrypt message for specific identity"""
        # Generate ephemeral key
        ephemeral_key = os.urandom(32)
        
        # Derive encryption key from identity
        identity_key = self._derive_encryption_key(identity, ephemeral_key)
        
        # Encrypt message using AES-GCM
        iv = os.urandom(12)
        cipher = Cipher(
            algorithms.AES(identity_key),
            modes.GCM(iv),
            backend=self.backend
        )
        encryptor = cipher.encryptor()
        
        ciphertext = encryptor.update(message) + encryptor.finalize()
        
        # Encrypt ephemeral key with master public key
        public_key = self.master_key.public_key()
        encrypted_ephemeral = public_key.encrypt(
            ephemeral_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        return {
            'ciphertext': base64.b64encode(ciphertext).decode(),
            'tag': base64.b64encode(encryptor.tag).decode(),
            'iv': base64.b64encode(iv).decode(),
            'ephemeral_key': base64.b64encode(encrypted_ephemeral).decode(),
            'identity': identity,
            'algorithm': 'AES-256-GCM-IBE'
        }
    
    def decrypt(self, encrypted_data: Dict, identity_key: bytes) -> bytes:
        """Decrypt message using identity key"""
        try:
            # Decode components
            ciphertext = base64.b64decode(encrypted_data['ciphertext'])
            tag = base64.b64decode(encrypted_data['tag'])
            iv = base64.b64decode(encrypted_data['iv'])
            encrypted_ephemeral = base64.b64decode(encrypted_data['ephemeral_key'])
            
            # Decrypt ephemeral key
            ephemeral_key = self.master_key.decrypt(
                encrypted_ephemeral,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            # Derive decryption key
            decryption_key = self._derive_encryption_key(
                encrypted_data['identity'],
                ephemeral_key
            )
            
            # Decrypt message
            cipher = Cipher(
                algorithms.AES(decryption_key),
                modes.GCM(iv, tag),
                backend=self.backend
            )
            decryptor = cipher.decryptor()
            
            plaintext = decryptor.update(ciphertext) + decryptor.finalize()
            
            return plaintext
            
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise
    
    def _derive_encryption_key(self, identity: str, ephemeral_key: bytes) -> bytes:
        """Derive encryption key from identity and ephemeral key"""
        from cryptography.hazmat.primitives.kdf.hkdf import HKDF
        
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'ibe-encryption',
            info=identity.encode(),
            backend=self.backend
        )
        
        return hkdf.derive(ephemeral_key)
    
    def encrypt_payment_data(self, payment_data: Dict, user_email: str) -> Dict:
        """Encrypt payment data for specific user"""
        # Serialize payment data
        data_bytes = json.dumps(payment_data).encode()
        
        # Encrypt with user's identity
        encrypted = self.encrypt(data_bytes, user_email)
        
        # Add metadata
        encrypted['encrypted_at'] = datetime.utcnow().isoformat()
        encrypted['data_type'] = 'payment_data'
        
        return encrypted
    
    def decrypt_payment_data(self, encrypted_data: Dict, user_email: str) -> Dict:
        """Decrypt payment data for user"""
        # Extract user's key
        identity_key = self.extract_key(user_email)
        
        # Decrypt
        decrypted_bytes = self.decrypt(encrypted_data, identity_key)
        
        # Parse JSON
        return json.loads(decrypted_bytes.decode())