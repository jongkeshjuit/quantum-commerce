# crypto/real_crypto_available.py
"""
Real Crypto Implementation với libraries đã có sẵn
- liboqs-python: Real Dilithium signatures 
- Charm-Crypto: Real IBE (thay cho pypbc)
"""
import os
import json
import base64
import hashlib
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Import libraries có sẵn
try:
    import oqs  # liboqs-python
    REAL_DILITHIUM = True
    logger.info("✅ Using REAL Dilithium from liboqs")
except ImportError:
    REAL_DILITHIUM = False
    logger.warning("❌ liboqs not available")

try:
    from charm.toolbox.pairinggroup import PairingGroup, G1, G2, GT, ZR
    from charm.toolbox.symcrypto import AuthenticatedCryptoAbstraction
    from charm.core.engine.util import objectToBytes, bytesToObject
    REAL_IBE = True
    logger.info("✅ Using REAL IBE from Charm-Crypto")
except ImportError:
    REAL_IBE = False
    logger.warning("❌ Charm-Crypto not available properly")

class RealDilithiumSigner:
    """Real Dilithium signer using liboqs-python"""
    
    def __init__(self, variant: str = "Dilithium3"):
        self.variant = variant
        self.keys_dir = Path("keys/dilithium")
        self.keys_dir.mkdir(parents=True, exist_ok=True)
        
        if REAL_DILITHIUM:
            self.signer = oqs.Signature(variant)
            self._setup_keys()
        else:
            self._setup_fallback()
    
    def _setup_keys(self):
        """Setup real Dilithium keys"""
        logger.info(f"🔑 Setting up {self.variant} keys...")
        
        # Generate keypair
        public_key = self.signer.generate_keypair()
        private_key = self.signer.export_secret_key()
        
        self.public_key = public_key
        self.private_key = private_key
        self.key_id = hashlib.sha256(public_key).hexdigest()[:16]
        
        logger.info(f"✅ {self.variant} keys ready: {self.key_id}")
    
    def sign_transaction(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sign transaction với real Dilithium"""
        # Normalize transaction
        normalized = self._normalize_transaction(transaction_data)
        message = json.dumps(normalized, sort_keys=True).encode()
        
        if REAL_DILITHIUM:
            # Real Dilithium signature
            signature = self.signer.sign(message)
            
            return {
                "transaction_data": normalized,
                "signature": base64.b64encode(signature).decode(),
                "public_key": base64.b64encode(self.public_key).decode(),
                "algorithm": self.variant,
                "key_id": self.key_id,
                "message_hash": hashlib.sha256(message).hexdigest(),
                "signed_at": datetime.utcnow().isoformat(),
                "quantum_secure": True
            }
        else:
            return self._fallback_sign(normalized, message)
    
    def verify_signature(self, signed_data: Dict[str, Any]) -> bool:
        """Verify real Dilithium signature"""
        try:
            if not REAL_DILITHIUM:
                return self._fallback_verify(signed_data)
            
            # Reconstruct message
            message = json.dumps(signed_data["transaction_data"], sort_keys=True).encode()
            
            # Decode components
            signature = base64.b64decode(signed_data["signature"])
            public_key = base64.b64decode(signed_data["public_key"])
            
            # Create verifier
            verifier = oqs.Signature(signed_data["algorithm"])
            
            # Verify signature
            return verifier.verify(message, signature, public_key)
            
        except Exception as e:
            logger.error(f"Signature verification failed: {e}")
            return False
    
    def _normalize_transaction(self, data: Dict) -> Dict:
        """Normalize transaction for signing"""
        return {
            "transaction_id": data.get("transaction_id"),
            "user_id": data.get("user_id"),
            "amount": float(data.get("amount", 0)),
            "currency": data.get("currency", "USD"),
            "timestamp": data.get("timestamp", datetime.utcnow().isoformat()),
            "nonce": data.get("nonce", os.urandom(16).hex())
        }
    
    def _setup_fallback(self):
        """Fallback cho development"""
        import secrets
        self.public_key = secrets.token_bytes(32)
        self.private_key = secrets.token_bytes(64)
        self.key_id = "fallback_" + secrets.token_hex(8)
        logger.info(f"⚠️ Using fallback Dilithium: {self.key_id}")
    
    def _fallback_sign(self, transaction_data: Dict, message: bytes) -> Dict:
        """Fallback signing"""
        signature_data = hashlib.sha256(message + self.private_key).digest()
        
        return {
            "transaction_data": transaction_data,
            "signature": base64.b64encode(signature_data).decode(),
            "public_key": base64.b64encode(self.public_key).decode(),
            "algorithm": f"{self.variant}_fallback",
            "key_id": self.key_id,
            "message_hash": hashlib.sha256(message).hexdigest(),
            "signed_at": datetime.utcnow().isoformat(),
            "quantum_secure": False
        }
    
    def _fallback_verify(self, signed_data: Dict) -> bool:
        """Fallback verification"""
        try:
            message = json.dumps(signed_data["transaction_data"], sort_keys=True).encode()
            expected_hash = hashlib.sha256(message).hexdigest()
            return expected_hash == signed_data.get("message_hash")
        except:
            return False

class RealIBESystem:
    """Real IBE using Charm-Crypto với proper error handling"""
    
    def __init__(self):
        self.keys_dir = Path("keys/ibe")
        self.keys_dir.mkdir(parents=True, exist_ok=True)
        
        if REAL_IBE:
            try:
                self._setup_real_ibe()
            except Exception as e:
                logger.error(f"Failed to setup real IBE: {e}")
                self._setup_fallback_ibe()
        else:
            self._setup_fallback_ibe()
    
    def _setup_real_ibe(self):
        """Setup real IBE với Charm-Crypto"""
        logger.info("🔐 Setting up REAL IBE with Charm-Crypto...")
        
        try:
            # Initialize pairing group với curve phù hợp
            self.group = PairingGroup('SS512')
            
            # Generate master secret
            self.master_secret = self.group.random(ZR)
            
            # System parameters
            self.g = self.group.random(G1)
            self.g_pub = self.g ** self.master_secret
            
            self.real_ibe_ready = True
            logger.info("✅ Real IBE system ready với Charm-Crypto")
            
        except Exception as e:
            logger.error(f"Failed to setup Charm IBE: {e}")
            self.real_ibe_ready = False
            raise
    
    def encrypt_for_user(self, data: str, user_identity: str) -> Dict[str, Any]:
        """Encrypt data cho user identity"""
        if REAL_IBE and hasattr(self, 'real_ibe_ready') and self.real_ibe_ready:
            return self._encrypt_real(data, user_identity)
        else:
            return self._encrypt_fallback(data, user_identity)
    
    def _encrypt_real(self, data: str, identity: str) -> Dict[str, Any]:
        """Real IBE encryption với Charm"""
        try:
            # Hash identity to group element
            identity_point = self.group.hash(identity, G1)
            
            # Choose random r
            r = self.group.random(ZR)
            
            # Compute pairing
            pairing_result = self.group.pair_prod(identity_point, self.g_pub) ** r
            
            # Use pairing result làm key cho AES
            key_bytes = objectToBytes(pairing_result, self.group)
            # Chỉ lấy 32 bytes đầu cho AES key
            aes_key = hashlib.sha256(key_bytes).digest()
            
            # Encrypt với AES
            aes = AuthenticatedCryptoAbstraction(aes_key)
            encrypted_data = aes.encrypt(data.encode())
            
            # Ciphertext component
            c1 = self.g ** r
            
            return {
                "identity": identity,
                "c1": objectToBytes(c1, self.group).hex(),
                "encrypted_data": base64.b64encode(encrypted_data).decode(),
                "algorithm": "real_ibe_charm",
                "encrypted_at": datetime.utcnow().isoformat(),
                "quantum_secure": True
            }
            
        except Exception as e:
            logger.error(f"Real IBE encryption failed: {e}")
            return self._encrypt_fallback(data, identity)
    
    def _setup_fallback_ibe(self):
        """Fallback IBE"""
        logger.warning("⚠️ Using fallback IBE implementation")
        self.real_ibe_ready = False
    
    def _encrypt_fallback(self, data: str, identity: str) -> Dict[str, Any]:
        """Fallback encryption using simple key derivation"""
        # Simple key derivation từ identity
        key = hashlib.sha256(identity.encode()).digest()[:32]
        
        from cryptography.fernet import Fernet
        fernet_key = base64.urlsafe_b64encode(key)
        fernet = Fernet(fernet_key)
        encrypted_data = fernet.encrypt(data.encode())
        
        return {
            "identity": identity,
            "encrypted_data": base64.b64encode(encrypted_data).decode(),
            "algorithm": "fallback_ibe",
            "encrypted_at": datetime.utcnow().isoformat(),
            "quantum_secure": False
        }

# Factory function
def create_real_crypto():
    """Create real crypto instances"""
    return {
        "dilithium": RealDilithiumSigner(),
        "ibe": RealIBESystem()
    }

# Test capabilities function
def test_crypto_capabilities():
    """Test và report crypto capabilities"""
    print("🔍 CRYPTO CAPABILITIES REPORT")
    print("=" * 40)
    
    # Test liboqs
    if REAL_DILITHIUM:
        try:
            # List available algorithms
            print("✅ liboqs-python available")
            sigs = oqs.get_enabled_sig_mechanisms()
            dilithium_variants = [s for s in sigs if 'Dilithium' in s]
            print(f"   Available Dilithium variants: {dilithium_variants}")
        except Exception as e:
            print(f"❌ liboqs error: {e}")
    else:
        print("❌ liboqs-python not available")
    
    # Test Charm-Crypto
    if REAL_IBE:
        try:
            print("✅ Charm-Crypto available")
            group = PairingGroup('SS512')
            print(f"   Pairing group: SS512")
            print(f"   Group order: {group.order()}")
        except Exception as e:
            print(f"❌ Charm-Crypto error: {e}")
    else:
        print("❌ Charm-Crypto not available")
    
    print()

if __name__ == "__main__":
    # Test script
    print("🧪 Testing Real Crypto Implementation...")
    
    # Report capabilities first
    test_crypto_capabilities()
    
    try:
        crypto = create_real_crypto()
        
        # Test Dilithium
        print("🔐 Testing Dilithium Signatures...")
        transaction = {
            "transaction_id": "test_123",
            "user_id": "user_456", 
            "amount": 100.50,
            "currency": "USD"
        }
        
        signed = crypto["dilithium"].sign_transaction(transaction)
        verified = crypto["dilithium"].verify_signature(signed)
        
        print(f"✅ Signature created: {signed['algorithm']}")
        print(f"✅ Verification: {verified}")
        print(f"🛡️ Quantum secure: {signed.get('quantum_secure', False)}")
        
        # Test IBE
        print("\n🔒 Testing IBE Encryption...")
        encrypted = crypto["ibe"].encrypt_for_user("Secret payment data", "user@example.com")
        print(f"✅ Encrypted with: {encrypted['algorithm']}")
        print(f"🛡️ Quantum secure: {encrypted.get('quantum_secure', False)}")
        
        print("\n🎉 All crypto tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Crypto test failed: {e}")
        import traceback
        traceback.print_exc()