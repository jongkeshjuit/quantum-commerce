#!/bin/bash
# Fixed setup script

echo "🚀 QUICK SETUP FOR TESTING (FIXED)"
echo "=================================="

# 1. Create .env file
echo "📝 Creating .env file..."
cat > .env << 'ENV_END'
# Quick setup for testing
APP_NAME=quantum-commerce
APP_ENV=development
DEBUG=true

# REQUIRED - Set passwords
DB_PASSWORD=quantum_secure_pass_123
REDIS_PASSWORD=redis_secure_pass_456
VAULT_TOKEN=dev_vault_token_789

# Database
DB_USER=quantum_user
DB_NAME=quantum_commerce
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Crypto
MASTER_PASSWORD=master_crypto_key_for_testing_only
USE_REAL_CRYPTO=true

# Features
RATE_LIMIT_ENABLED=true
SESSION_TIMEOUT_MINUTES=30

# Monitoring
GRAFANA_PASSWORD=grafana_admin_123
ENV_END

# 2. Create simple docker-compose
echo "🔧 Creating docker-compose-simple.yml..."
cat > docker-compose-simple.yml << 'COMPOSE_END'
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: qc_postgres_new
    environment:
      POSTGRES_USER: quantum_user
      POSTGRES_PASSWORD: quantum_secure_pass_123
      POSTGRES_DB: quantum_commerce
    ports:
      - "5432:5432"
    volumes:
      - postgres_data_new:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    container_name: qc_redis_new
    command: redis-server --requirepass redis_secure_pass_456
    ports:
      - "6379:6379"
    volumes:
      - redis_data_new:/data

  vault:
    image: hashicorp/vault:1.15
    container_name: qc_vault_new
    cap_add:
      - IPC_LOCK
    environment:
      VAULT_DEV_ROOT_TOKEN_ID: dev_vault_token_789
      VAULT_DEV_LISTEN_ADDRESS: 0.0.0.0:8200
    ports:
      - "8200:8200"
    command: vault server -dev

volumes:
  postgres_data_new:
  redis_data_new:
COMPOSE_END

echo "✅ Setup files created!"
