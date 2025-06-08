# test_config.py
from config.dev_config import SecurityConfig

def test_security_config():
    print("🔧 Testing Security Configuration...")
    
    # Test basic methods
    try:
        master_key = SecurityConfig.get_master_key()
        print(f"✅ Master key: {len(master_key)} bytes")
    except Exception as e:
        print(f"❌ Master key error: {e}")
    
    try:
        fernet = SecurityConfig.get_fernet_key()
        test_data = b"Hello Quantum World"
        encrypted = fernet.encrypt(test_data)
        decrypted = fernet.decrypt(encrypted)
        print(f"✅ Fernet encryption: {decrypted == test_data}")
    except Exception as e:
        print(f"❌ Fernet error: {e}")
    
    try:
        redis_url = SecurityConfig.get_redis_url()
        print(f"✅ Redis URL: {redis_url}")
    except Exception as e:
        print(f"❌ Redis URL error: {e}")
    
    try:
        db_url = SecurityConfig.get_database_url()
        print(f"✅ Database URL: {db_url.split('@')[0]}@***")
    except Exception as e:
        print(f"❌ Database URL error: {e}")
    
    # Validate configuration
    validation = SecurityConfig.validate_config()
    print(f"\n📋 Configuration Status:")
    print(f"Valid: {validation['valid']}")
    if validation['issues']:
        print(f"Issues: {validation['issues']}")
    if validation['warnings']:
        print(f"Warnings: {validation['warnings']}")

if __name__ == "__main__":
    test_security_config()