"""
Crypto module initialization
Automatically selects real or mock implementation based on environment
"""
import os
from config.security import SecurityConfig

# Check if we should use real implementations
USE_REAL_CRYPTO = os.getenv('USE_REAL_CRYPTO', 'true').lower() == 'true'

if USE_REAL_CRYPTO and SecurityConfig.APP_ENV != 'test':
    try:
        from .real_dilithium import RealDilithiumSigner as DilithiumSigner
        from .real_ibe import RealIBESystem as IBESystem
        print("Using REAL cryptographic implementations")
    except ImportError as e:
        print(f"Failed to import real crypto: {e}")
        print("Falling back to mock implementations")
        # Sửa tên class ở đây
        from .mock_implementations import DilithiumSigner
        from .mock_implementations import IBESystem
else:
    # Sửa tên class ở đây
    from .mock_implementations import DilithiumSigner
    from .mock_implementations import IBESystem
    print("Using MOCK cryptographic implementations")

__all__ = ['DilithiumSigner', 'IBESystem']