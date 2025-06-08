# test_final.py
from config.dev_config import SecurityConfig
from config.database import DatabaseConfig

def test_all_configs():
    print("🔧 Testing All Configurations...")
    
    # Test SecurityConfig
    print("\n📋 SecurityConfig Tests:")
    print(f"✅ JWT_ALGORITHM: {SecurityConfig.JWT_ALGORITHM}")
    print(f"✅ JWT_SECRET: {SecurityConfig.get_jwt_secret()[:10]}...")
    
    # Test properties (the problematic ones)
    sc = SecurityConfig()
    try:
        redis_url = sc.REDIS_URL
        print(f"✅ REDIS_URL property: {redis_url}")
    except Exception as e:
        print(f"❌ REDIS_URL error: {e}")
    
    # Test DatabaseConfig
    print("\n📋 DatabaseConfig Tests:")
    try:
        db_url = DatabaseConfig.get_database_url()
        print(f"✅ DatabaseConfig URL: {db_url.split('@')[0]}@***")
    except Exception as e:
        print(f"❌ DatabaseConfig error: {e}")
    
    # Test crypto keys
    print("\n🔐 Crypto Keys:")
    keys = SecurityConfig.get_crypto_keys()
    for key, value in keys.items():
        print(f"✅ {key}: {value[:10]}...")
    
    print("\n🎯 All tests completed!")

if __name__ == "__main__":
    test_all_configs()