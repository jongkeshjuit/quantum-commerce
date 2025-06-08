# scripts/test_vault_connection.py
#!/usr/bin/env python3
"""
Test Vault connection and secrets
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set environment
os.environ['VAULT_ADDR'] = 'http://localhost:8200'
os.environ['VAULT_TOKEN'] = 'myroot'

from config.vault_config import vault_client

def test_vault():
    print("🔐 Testing Vault Connection...")
    
    if not vault_client.client:
        print("❌ Vault client not initialized")
        return False
    
    print("✅ Vault connected")
    
    # Test reading secrets
    secrets_to_test = [
        'quantum-commerce/ibe_master_key',
        'quantum-commerce/dilithium_master_key',
        'quantum-commerce/database_encryption_key',
        'quantum-commerce/jwt_secret_key'
    ]
    
    for secret_path in secrets_to_test:
        value = vault_client.get_secret(secret_path)
        if value:
            print(f"✅ Found secret: {secret_path} (length: {len(value)})")
        else:
            print(f"❌ Missing secret: {secret_path}")
    
    # Test writing
    test_value = "test_value_123"
    if vault_client.store_secret("quantum-commerce/test", test_value):
        retrieved = vault_client.get_secret("quantum-commerce/test")
        if retrieved == test_value:
            print("✅ Write/Read test passed")
        else:
            print("❌ Write/Read test failed")
    
    return True

if __name__ == "__main__":
    try:
        test_vault()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()