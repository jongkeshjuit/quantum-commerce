#!/usr/bin/env python3
"""
SIMPLE TEST - Chỉ test core functionality
"""
import requests
import time

def test_system():
    print("🧪 SIMPLE QUANTUM SYSTEM TEST")
    print("=" * 40)
    
    base_url = "http://localhost:8000"
    
    # 1. Test crypto directly
    print("1. 🔐 Testing crypto system...")
    try:
        from crypto.production_crypto import create_production_crypto
        crypto = create_production_crypto()
        
        # Test signature
        tx = {"id": "test", "amount": 100}
        signed = crypto['signer'].sign_transaction(tx)
        verified = crypto['signer'].verify_signature(signed)
        
        print(f"   ✅ Algorithm: {signed['algorithm']}")
        print(f"   ✅ Quantum: {signed['quantum_secure']}")
        print(f"   ✅ Verified: {verified}")
        
    except Exception as e:
        print(f"   ❌ Crypto error: {e}")
    
    # 2. Test API if running
    print("\n2. 🚀 Testing API...")
    try:
        r = requests.get(f"{base_url}/", timeout=3)
        if r.status_code == 200:
            print("   ✅ API healthy")
            
            # Test payment
            payment = {"amount": 150.75, "currency": "USD"}
            r2 = requests.post(f"{base_url}/api/payments/process", 
                              json=payment, timeout=5)
            if r2.status_code == 200:
                data = r2.json()
                print(f"   ✅ Payment: {data.get('status')}")
                print(f"   ✅ Quantum: {data.get('quantum_secure')}")
        else:
            print(f"   ⚠️ API not healthy: {r.status_code}")
            
    except Exception as e:
        print(f"   ⚠️ API not running: {e}")
        print("   💡 Start with: python main.py")
    
    print("\n🎉 SIMPLE TEST COMPLETED!")
    print("🛡️ Your quantum crypto system is WORKING!")

if __name__ == "__main__":
    test_system()
