# """
# Quantum-Secure Crypto Module
# Real Dilithium + Enhanced IBE
# """
# from .production_crypto import (
#     QuantumSecureSigner,
#     EnhancedIBESystem,
#     create_production_crypto,
#     get_crypto_status
# )

# # Backward compatibility
# from .production_crypto import QuantumSecureSigner as DilithiumSigner
# from .production_crypto import EnhancedIBESystem as IBESystem

# __all__ = [
#     'QuantumSecureSigner',
#     'DilithiumSigner', 
#     'EnhancedIBESystem',
#     'IBESystem',
#     'create_production_crypto',
#     'get_crypto_status'
# ]

# # Initialize global crypto instances
# crypto_instances = create_production_crypto()
# signer = crypto_instances['signer']
# ibe_system = crypto_instances['ibe']

# print("🛡️ Quantum-Secure Crypto Module Loaded")
# print(f"   Signer: {signer.variant}")
# print(f"   Quantum Secure: {getattr(signer, 'REAL_DILITHIUM', False)}")

# crypto/__init__.py
from .production_crypto import (
    QuantumSecureSigner,
    EnhancedIBESystem,
    create_production_crypto,
    get_crypto_status
)

# Aliases for backward compatibility
DilithiumSigner = QuantumSecureSigner
IBESystem = EnhancedIBESystem

# Singleton
_crypto_instances = None

def get_crypto():
    global _crypto_instances
    if not _crypto_instances:
        _crypto_instances = create_production_crypto()
    return _crypto_instances

# Optional eager init for CLI/demo
if __name__ == "__main__":  # or use an ENV VAR to control this
    _crypto = get_crypto()
    signer = _crypto['signer']
    ibe_system = _crypto['ibe']
    print("🛡️ Quantum-Secure Crypto Module Loaded")
    print(f"   Signer: {signer.variant}")
    print(f"   Quantum Secure: {getattr(signer, 'REAL_DILITHIUM', False)}")

__all__ = [
    'QuantumSecureSigner', 'DilithiumSigner',
    'EnhancedIBESystem', 'IBESystem',
    'create_production_crypto', 'get_crypto_status',
    'get_crypto'
]
