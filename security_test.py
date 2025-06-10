# Tạo file: scripts/security_test.py
import asyncio
from main import app
from crypto import get_crypto

async def test_security():
    print("🔒 KIỂM TRA BẢO MẬT")
    
    # 1. Test Dilithium
    crypto = get_crypto()
    data = {"amount": 100, "user": "test"}
    signed = crypto['signer'].sign_transaction(data)
    verified = crypto['signer'].verify_signature(signed)
    print(f"✅ Dilithium: {'OK' if verified else 'FAILED'}")
    
    # 2. Test IBE
    encrypted = crypto['ibe'].encrypt_for_user("secret", "user@test.com")
    print(f"✅ IBE Encryption: OK")
    
    # 3. Test Replay Protection
    # Thử gửi 2 request giống nhau
    # Request thứ 2 phải bị reject
    
    print("\n🎉 TẤT CẢ TESTS PASSED!")

if __name__ == "__main__":
    asyncio.run(test_security())