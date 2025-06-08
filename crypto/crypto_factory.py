# crypto/crypto_factory.py
"""
Factory pattern for crypto implementations
"""
from typing import Protocol, Dict, Any
import logging

logger = logging.getLogger(__name__)

class SignerProtocol(Protocol):
    """Protocol for digital signature implementations"""
    def sign_transaction(self, transaction_data: Dict) -> Dict:
        ...
    
    def verify_transaction(self, signed_transaction: Dict) -> bool:
        ...

class CryptoFactory:
    """Factory for creating crypto implementations"""
    
    @staticmethod
    def create_signer(use_real: bool = True) -> SignerProtocol:
        if use_real:
            try:
                from .real_dilithium import RealDilithiumSigner
                logger.info("Creating real Dilithium signer")
                return RealDilithiumSigner()
            except Exception as e:
                logger.error(f"Failed to create real signer: {e}")
        
        from .dilithium_signer import DilithiumSigner
        logger.info("Creating mock Dilithium signer")
        return DilithiumSigner()