# scripts/setup_vault.sh
#!/bin/bash
set -e

echo "🔐 Setting up HashiCorp Vault..."

# Set Vault address for commands
export VAULT_ADDR='http://localhost:8200'

# Wait for Vault to be ready
until curl -s http://localhost:8200/v1/sys/health &>/dev/null; do
    echo "Waiting for Vault to be ready..."
    sleep 2
done

echo "✅ Vault is ready!"

# Login with dev root token
docker exec qc_vault vault login -address=http://localhost:8200 myroot

# Enable KV v2 secrets engine (if not exists)
echo "📦 Enabling KV v2 secrets engine..."
docker exec -e VAULT_ADDR=http://localhost:8200 qc_vault vault secrets enable -version=2 -path=secret kv 2>/dev/null || echo "KV v2 already enabled"

# Create quantum-commerce path
docker exec -e VAULT_ADDR=http://localhost:8200 qc_vault vault kv put secret/quantum-commerce/config \
    initialized=true \
    timestamp="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

# Generate and store master keys
echo "🔑 Generating master keys..."

# IBE Master Key
IBE_KEY=$(openssl rand -base64 32)
docker exec -e VAULT_ADDR=http://localhost:8200 qc_vault vault kv put secret/quantum-commerce/ibe_master_key \
    value="$IBE_KEY"

# Dilithium Master Key  
DILITHIUM_KEY=$(openssl rand -base64 64)
docker exec -e VAULT_ADDR=http://localhost:8200 qc_vault vault kv put secret/quantum-commerce/dilithium_master_key \
    value="$DILITHIUM_KEY"

# Database Encryption Key
DB_KEY=$(python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
docker exec -e VAULT_ADDR=http://localhost:8200 qc_vault vault kv put secret/quantum-commerce/database_encryption_key \
    value="$DB_KEY"

# JWT Secret
JWT_SECRET=$(openssl rand -base64 32)
docker exec -e VAULT_ADDR=http://localhost:8200 qc_vault vault kv put secret/quantum-commerce/jwt_secret_key \
    value="$JWT_SECRET"

echo "✅ Master keys generated and stored in Vault"

# Verify keys were stored
echo ""
echo "📋 Verifying stored secrets..."
docker exec -e VAULT_ADDR=http://localhost:8200 qc_vault vault kv list secret/quantum-commerce

echo ""
echo "✅ Vault setup completed!"
echo ""
echo "📝 Important information:"
echo "   Vault Address: http://localhost:8200"
echo "   Root Token: myroot"
echo "   Keys are stored at: secret/quantum-commerce/*"