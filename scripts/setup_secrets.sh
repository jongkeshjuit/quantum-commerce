#!/bin/bash

echo "🔐 Setting up Quantum Commerce Secrets"
echo "======================================"

# Tạo thư mục secrets
mkdir -p secrets
chmod 700 secrets

# Generate master password nếu chưa có
if [ -z "$MASTER_PASSWORD" ]; then
    echo "⚠️ MASTER_PASSWORD not set in environment"
    echo "Generating random master password..."
    MASTER_PASSWORD=$(openssl rand -base64 32)
    echo "export MASTER_PASSWORD='$MASTER_PASSWORD'" >> ~/.bashrc
    echo "✅ Master password generated and saved to ~/.bashrc"
    echo "🔄 Run: source ~/.bashrc"
fi

# Generate secrets
echo "🔑 Generating cryptographic secrets..."

# JWT Secret
JWT_SECRET=$(openssl rand -base64 32)
echo "export JWT_SECRET_KEY='$JWT_SECRET'" >> .env.local

# Dilithium Master Key  
DILITHIUM_KEY=$(openssl rand -base64 64)
echo "export DILITHIUM_MASTER_KEY='$DILITHIUM_KEY'" >> .env.local

# IBE Master Key
IBE_KEY=$(openssl rand -base64 32)
echo "export IBE_MASTER_KEY='$IBE_KEY'" >> .env.local

# Database password
DB_PASS=$(openssl rand -base64 24)
echo "export DB_PASSWORD='$DB_PASS'" >> .env.local

# Redis password
REDIS_PASS=$(openssl rand -base64 24)
echo "export REDIS_PASSWORD='$REDIS_PASS'" >> .env.local

echo ""
echo "✅ Secrets generated in .env.local"
echo "🔒 Load them with: source .env.local"
echo ""
echo "⚠️ IMPORTANT SECURITY NOTES:"
echo "1. NEVER commit .env.local to git"
echo "2. In production, use environment variables or Vault"
echo "3. Rotate keys every 90 days"
echo "4. Backup encrypted secrets securely"
echo ""
echo "🔄 Next: source .env.local && python main.py"