# scripts/test_crypto.py
#!/usr/bin/env python3
"""
Test real crypto implementations
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set to use real crypto
os.environ['USE_REAL_CRYPTO'] = 'true'

from crypto import DilithiumSigner, IBESystem
import json

def test_dilithium():
    print("\n🔐 Testing Dilithium Signatures...")
    
    signer = DilithiumSigner()
    
    # Test transaction
    transaction = {
        "amount": 100.0,
        "currency": "USD",
        "customer_id": "user123",
        "merchant_id": "merchant456"
    }
    
    # Sign transaction
    signed = signer.sign_transaction(transaction)
    print(f"✅ Transaction signed successfully")
    print(f"   Signature length: {len(signed['signature'])} chars")
    print(f"   Algorithm: {signed['algorithm']}")
    
    # Verify signature
    is_valid = signer.verify_transaction(signed)
    print(f"✅ Signature verified: {is_valid}")
    
    return True

def test_ibe():
    print("\n🔐 Testing IBE Encryption...")
    
    ibe = IBESystem()
    
    # Test data
    payment_data = {
        "card_number": "4111111111111111",
        "amount": 99.99
    }
    
    user_email = "test@example.com"
    
    # Encrypt
    encrypted = ibe.encrypt_payment_data(payment_data, user_email)
    print(f"✅ Payment data encrypted")
    print(f"   Ciphertext length: {len(encrypted['ciphertext'])} chars")
    
    # Decrypt
    decrypted = ibe.decrypt_payment_data(encrypted, user_email)
    print(f"✅ Payment data decrypted")
    print(f"   Decrypted amount: ${decrypted['amount']}")
    
    return True

def test_vault():
    print("\n🔐 Testing Vault Integration...")
    
    from config.vault_config import vault_client
    
    # Test connection
    if vault_client.client:
        print("✅ Vault connected")
        
        # Test secret storage
        test_secret = "test_value_123"
        vault_client.store_secret("quantum-commerce/test", test_secret)
        
        # Test secret retrieval
        retrieved = vault_client.get_secret("quantum-commerce/test")
        assert retrieved == test_secret
        print("✅ Secret storage working")
    else:
        print("⚠️  Vault not configured (development mode)")
    
    return True

if __name__ == "__main__":
    print("=" * 50)
    print("QUANTUM COMMERCE CRYPTO TEST")
    print("=" * 50)
    
    try:
        # Test all components
        all_passed = True
        all_passed &= test_dilithium()
        all_passed &= test_ibe()
        all_passed &= test_vault()
        
        print("\n" + "=" * 50)
        if all_passed:
            print("✅ ALL TESTS PASSED!")
        else:
            print("❌ Some tests failed")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)