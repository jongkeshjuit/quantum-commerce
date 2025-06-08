import pytest
from crypto import DilithiumSigner, IBESystem
from auth.password_manager import PasswordManager
from security.rate_limiter import RateLimiter

def test_dilithium_signature():
    """Test Dilithium signature generation and verification"""
    signer = DilithiumSigner()
    
    # Generate keypair first
    public_key, secret_key, key_id = signer.generate_keypair()
    
    # Test data
    transaction = {
        "merchant_id": "merchant_123",
        "customer_id": "customer_456", 
        "amount": 100.0,
        "currency": "USD",
        "items": [{"id": "1", "name": "Test Item", "price": 100.0}]
    }
    
    # Sign with correct parameters
    signed = signer.sign_transaction(transaction, secret_key, key_id)
    
    assert signed.transaction_id is not None
    assert signed.amount == 100.0
    assert signed.signature is not None
    print("✓ Dilithium signature test passed")

def test_ibe_encryption():
    """Test IBE encryption and decryption"""
    ibe = IBESystem()
    
    # Get public params first
    public_params = ibe.get_public_params()
    
    # Test data
    message = b"Secret payment data"
    identity = "user@example.com"
    
    # Encrypt with correct parameters
    encrypted = ibe.encrypt(message, identity, public_params)
    
    assert encrypted is not None
    assert len(encrypted) > 0
    print("✓ IBE encryption test passed")

def test_password_hashing():
    """Test password hashing and verification"""
    pm = PasswordManager()
    
    password = "Test@123456"
    hashed = pm.hash_password(password)
    
    assert pm.verify_password(password, hashed)
    assert not pm.verify_password("wrong_password", hashed)
    print("✓ Password hashing test passed")

def test_rate_limiting():
    """Test rate limiting functionality"""
    limiter = RateLimiter()
    
    # Should allow first request
    assert limiter.check_rate_limit("test_user", "login") == True
    print("✓ Rate limiting test passed")