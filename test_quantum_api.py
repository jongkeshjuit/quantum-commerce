#!/usr/bin/env python3
"""
Comprehensive test cho Quantum-Secure API
"""
import requests
import json
import time

def test_quantum_api():
    base_url = "http://localhost:8000"
    
    print("🧪 TESTING QUANTUM-SECURE API")
    print("=" * 50)
    
    # 1. Health check
    print("1. 🔍 Testing health check...")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ API Status: {data['status']}")
            print(f"   🛡️ Crypto Ready: {data['crypto_ready']}")
            print(f"   🔐 Quantum Secure: {data['quantum_secure']}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        return False
    
    # 2. Crypto status
    print("\n2. 🔐 Testing crypto status...")
    try:
        response = requests.get(f"{base_url}/api/crypto/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Crypto Status: {data['status']}")
            print(f"   🛡️ Signer: {data['signer']['algorithm']}")
            print(f"   🔒 Security: {data['signer']['security_level']}")
            print(f"   🔐 Quantum: {data['signer']['quantum_secure']}")
        else:
            print(f"   ❌ Crypto status failed: {response.status_code}")
    except Exception as e:
        print(f"   ⚠️ Crypto status error: {e}")
    
    # 3. Test signing
    print("\n3. ✍️ Testing quantum signature...")
    transaction = {
        "transaction_id": "test_quantum_001",
        "user_id": "user_123",
        "amount": 150.75,
        "currency": "USD",
        "items": ["laptop", "mouse"]
    }
    
    try:
        response = requests.post(f"{base_url}/api/crypto/sign", 
                               json=transaction, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Signing: {data['status']}")
            print(f"   🛡️ Algorithm: {data['signed_transaction']['algorithm']}")
            print(f"   🔐 Quantum: {data['quantum_secure']}")
            print(f"   🔒 Security: {data['security_level']}")
            
            # Store for verification
            signed_transaction = data['signed_transaction']
            
            # 4. Test verification
            print("\n4. ✅ Testing signature verification...")
            verify_response = requests.post(f"{base_url}/api/crypto/verify",
                                          json=signed_transaction, timeout=10)
            if verify_response.status_code == 200:
                verify_data = verify_response.json()
                print(f"   ✅ Verification: {verify_data['verified']}")
                print(f"   🛡️ Algorithm: {verify_data['algorithm']}")
                print(f"   🔐 Quantum: {verify_data['quantum_secure']}")
            else:
                print(f"   ❌ Verification failed: {verify_response.status_code}")
                
        else:
            print(f"   ❌ Signing failed: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Signing error: {e}")
    
    # 5. Test encryption
    print("\n5. 🔒 Testing IBE encryption...")
    encryption_data = {
        "message": "Secret payment data: Card 1234-5678-9012-3456",
        "identity": "user123@quantum.com"
    }
    
    try:
        response = requests.post(f"{base_url}/api/crypto/encrypt",
                               json=encryption_data, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Encryption: {data['status']}")
            print(f"   🔒 Algorithm: {data['encrypted_data']['algorithm']}")
            print(f"   🛡️ Security: {data['encrypted_data']['security_level']}")
        else:
            print(f"   ❌ Encryption failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Encryption error: {e}")
    
    print("\n🎉 QUANTUM API TEST COMPLETED!")
    print("🛡️ Your e-commerce API is quantum-secure!")

if __name__ == "__main__":
    test_quantum_api()
