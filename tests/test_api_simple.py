#!/usr/bin/env python3
"""
Simple API test để kiểm tra hệ thống
"""
import requests
import json
import time

def test_api():
    base_url = "http://localhost:8000"
    
    print("🧪 TESTING QUANTUM COMMERCE API")
    print("=" * 40)
    
    # 1. Health check
    print("1. Testing health check...")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("   ✅ API is running")
        else:
            print(f"   ❌ API returned {response.status_code}")
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        return False
    
    # 2. Crypto endpoints
    print("2. Testing crypto endpoints...")
    try:
        response = requests.get(f"{base_url}/api/crypto/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Crypto status: {data}")
        else:
            print(f"   ⚠️ Crypto endpoint: {response.status_code}")
    except Exception as e:
        print(f"   ⚠️ Crypto test: {e}")
    
    # 3. Register test user
    print("3. Testing user registration...")
    test_user = {
        "email": "test@quantum.com",
        "username": "testuser",
        "password": "TestPass123!",
        "full_name": "Test User"
    }
    
    try:
        response = requests.post(f"{base_url}/api/auth/register", 
                               json=test_user, timeout=10)
        if response.status_code == 200:
            print("   ✅ Registration successful")
        else:
            print(f"   ⚠️ Registration: {response.status_code} - {response.text[:100]}")
    except Exception as e:
        print(f"   ⚠️ Registration test: {e}")
    
    print("\n🎉 Basic API test completed!")
    return True

if __name__ == "__main__":
    test_api()
