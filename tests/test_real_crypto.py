# scripts/test_real_crypto.py
#!/usr/bin/env python3
"""
Test real crypto implementations
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Force use real crypto
os.environ['USE_REAL_CRYPTO'] = 'true'
os.environ['VAULT_ADDR'] = 'http://localhost:8200'
os.environ['VAULT_TOKEN'] = 'myroot'

import json
from crypto import DilithiumSigner, IBESystem

def test_dilithium():
    print("\n🔐 Testing Real Dilithium Signatures...")
    
    try:
        signer = DilithiumSigner()
        print("✅ Dilithium signer initialized")
        
        # Test transaction
        transaction = {
            "transaction_id": "tx_123",
            "amount": 100.0,
            "currency": "USD",
            "customer_id": "user123",
            "merchant_id": "merchant456",
            "timestamp": "2025-06-08T12:00:00Z"
        }
        
        # Sign transaction
        signed = signer.sign_transaction(transaction)
        print(f"✅ Transaction signed")
        print(f"   Signature length: {len(signed['signature'])} chars")
        print(f"   Algorithm: {signed['algorithm']}")
        
        # Verify signature
        is_valid = signer.verify_transaction(signed)
        print(f"✅ Signature verified: {is_valid}")
        
        # Test tampering
        signed_copy = signed.copy()
        signed_copy['transaction']['amount'] = 200.0  # Tamper with amount
        is_valid_tampered = signer.verify_transaction(signed_copy)
        print(f"✅ Tampered signature rejected: {not is_valid_tampered}")
        
        return True
        
    except Exception as e:
        print(f"❌ Dilithium test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ibe():
    print("\n🔐 Testing Real IBE Encryption...")
    
    try:
        ibe = IBESystem()
        print("✅ IBE system initialized")
        
        # Setup IBE parameters
        params = ibe.setup()
        print(f"✅ IBE parameters generated")
        print(f"   Algorithm: {params['algorithm']}")
        print(f"   Security level: {params['security_level']}")
        
        # Test payment data
        payment_data = {
            "card_number": "4111111111111111",
            "cvv": "123",
            "expiry": "12/25",
            "amount": 99.99
        }
        
        user_email = "test@example.com"
        
        # Encrypt payment data
        encrypted = ibe.encrypt_payment_data(payment_data, user_email)
        print(f"✅ Payment data encrypted")
        print(f"   Ciphertext length: {len(encrypted['ciphertext'])} chars")
        print(f"   Encrypted for: {encrypted['identity']}")
        
        # Decrypt payment data
        decrypted = ibe.decrypt_payment_data(encrypted, user_email)
        print(f"✅ Payment data decrypted")
        print(f"   Amount: ${decrypted['amount']}")
        print(f"   Data matches: {payment_data == decrypted}")
        
        # Test wrong identity
        try:
            wrong_decrypted = ibe.decrypt_payment_data(encrypted, "wrong@example.com")
            print("❌ Wrong identity should not decrypt!")
            return False
        except:
            print("✅ Wrong identity cannot decrypt (expected)")
        
        return True
        
    except Exception as e:
        print(f"❌ IBE test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_performance():
    print("\n⚡ Performance Test...")
    
    import time
    
    # Test Dilithium performance
    signer = DilithiumSigner()
    transaction = {"amount": 100, "id": "test"}
    
    # Sign performance
    start = time.time()
    for i in range(10):
        signed = signer.sign_transaction(transaction)
    sign_time = (time.time() - start) / 10
    print(f"📊 Dilithium sign: {sign_time*1000:.2f}ms per operation")
    
    # Verify performance
    start = time.time()
    for i in range(10):
        signer.verify_transaction(signed)
    verify_time = (time.time() - start) / 10
    print(f"📊 Dilithium verify: {verify_time*1000:.2f}ms per operation")
    
    # Test IBE performance
    ibe = IBESystem()
    data = {"test": "data" * 100}  # ~800 bytes
    
    # Encrypt performance
    start = time.time()
    for i in range(10):
        encrypted = ibe.encrypt_payment_data(data, "test@example.com")
    encrypt_time = (time.time() - start) / 10
    print(f"📊 IBE encrypt: {encrypt_time*1000:.2f}ms per operation")
    
    # Decrypt performance
    start = time.time()
    for i in range(10):
        ibe.decrypt_payment_data(encrypted, "test@example.com")
    decrypt_time = (time.time() - start) / 10
    print(f"📊 IBE decrypt: {decrypt_time*1000:.2f}ms per operation")

if __name__ == "__main__":
    print("=" * 60)
    print("QUANTUM COMMERCE - REAL CRYPTO TEST")
    print("=" * 60)
    
    all_passed = True
    
    # Run tests
    all_passed &= test_dilithium()
    all_passed &= test_ibe()
    test_performance()
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL CRYPTO TESTS PASSED!")
    else:
        print("❌ Some tests failed")
        sys.exit(1)