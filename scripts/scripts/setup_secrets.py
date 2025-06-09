#!/usr/bin/env python3
"""
Setup secrets securely - RUN ONCE sau khi deploy
"""
import sys
import getpass
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.secret_manager import secret_manager

def setup_production_secrets():
    """Setup secrets cho production"""
    print("🔐 Quantum Commerce - Secret Setup")
    print("=" * 40)
    
    # Yêu cầu user nhập passwords
    secrets = {}
    
    print("\n📝 Nhập các passwords (sẽ được mã hóa và lưu an toàn):")
    
    secrets['database_password'] = getpass.getpass("Database password: ")
    secrets['redis_password'] = getpass.getpass("Redis password: ")
    secrets['jwt_secret'] = secret_manager._generate_jwt_key()
    
    print("\n🔑 Generating crypto keys...")
    secrets['dilithium_master_key'] = secret_manager._generate_dilithium_key()
    secrets['ibe_master_key'] = secret_manager._generate_ibe_key()
    secrets['database_encryption_key'] = secret_manager._generate_db_key()
    
    print("\n💾 Storing secrets securely...")
    success_count = 0
    for key, value in secrets.items():
        if secret_manager.store_secret(key, value):
            print(f"✅ {key}")
            success_count += 1
        else:
            print(f"❌ {key}")
    
    print(f"\n🎯 Setup completed: {success_count}/{len(secrets)} secrets stored")
    
    if success_count == len(secrets):
        print("✅ All secrets stored successfully!")
        print("\n⚠️  IMPORTANT:")
        print("- Backup your Vault/secrets safely")
        print("- Never commit secrets to git")
        print("- Rotate keys regularly")
    else:
        print("❌ Some secrets failed to store. Check logs.")

if __name__ == "__main__":
    setup_production_secrets()