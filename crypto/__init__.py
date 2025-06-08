"""
Quantum-Secure Crypto Module
Real Dilithium + Enhanced IBE
"""
from .production_crypto import (
    QuantumSecureSigner,
    EnhancedIBESystem,
    create_production_crypto,
    get_crypto_status
)

# Backward compatibility
from .production_crypto import QuantumSecureSigner as DilithiumSigner
from .production_crypto import EnhancedIBESystem as IBESystem

__all__ = [
    'QuantumSecureSigner',
    'DilithiumSigner', 
    'EnhancedIBESystem',
    'IBESystem',
    'create_production_crypto',
    'get_crypto_status'
]

# Initialize global crypto instances
crypto_instances = create_production_crypto()
signer = crypto_instances['signer']
ibe_system = crypto_instances['ibe']

print("🛡️ Quantum-Secure Crypto Module Loaded")
print(f"   Signer: {signer.variant}")
print(f"   Quantum Secure: {getattr(signer, 'REAL_DILITHIUM', False)}")
