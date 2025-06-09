#!/bin/bash
# Quick Development Setup - Skip production secrets

echo "🚀 QUICK DEVELOPMENT SETUP"
echo "=========================="

# 1. Create .env for development
cat > .env << 'EOF'
# DEVELOPMENT ENVIRONMENT
APP_NAME=quantum-commerce
APP_ENV=development
DEBUG=true

# Skip production secrets
USE_REAL_CRYPTO=false
USE_ENCRYPTED_SECRETS=false

# Database - Match docker containers
DB_HOST=localhost
DB_PORT=5432
DB_USER=quantum_user
DB_PASSWORD=quantum_secure_pass_123
DB_NAME=quantum_commerce

# Redis - Match docker containers
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=redis_secure_pass_456

# Vault
VAULT_ADDR=http://localhost:8200
VAULT_TOKEN=dev_vault_token_789

# Development master password (any value)
MASTER_PASSWORD=test_master_key_123

# Features
RATE_LIMIT_ENABLED=true
SESSION_TIMEOUT_MINUTES=30

# Monitoring
PROMETHEUS_HOST=localhost
PROMETHEUS_PORT=9090
GRAFANA_HOST=localhost  
GRAFANA_PORT=3030
GRAFANA_PASSWORD=quantum_admin_123
EOF

echo "✅ Created .env for development"

# 2. Set environment
export MASTER_PASSWORD=test_master_key_123
export APP_ENV=development
export USE_REAL_CRYPTO=false

echo "✅ Environment variables set"

# 3. Fix encryption error
# if [ -f "database/encryption.py" ]; then
#     sed -i 's/SecurityConfig.get_fernet_key()()/SecurityConfig.get_fernet_key()/g' database/encryption.py
#     echo "✅ Fixed encryption.py"
# fi

# 4. Test database connection
echo "🔍 Testing database connection..."
python3 -c "
import psycopg2
try:
    conn = psycopg2.connect(
        host='localhost', port=5432,
        user='quantum_user', 
        password='quantum_secure_pass_123',
        database='quantum_commerce'
    )
    print('✅ PostgreSQL: Connected!')
    conn.close()
except Exception as e:
    print(f'❌ PostgreSQL: {e}')
"

# 5. Test Redis
echo "🔍 Testing Redis connection..."
python3 -c "
import redis
try:
    r = redis.Redis(host='localhost', port=6379, password='redis_secure_pass_456')
    r.ping()
    print('✅ Redis: Connected!')
except Exception as e:
    print(f'❌ Redis: {e}')
"

# 6. Test imports
echo "🔍 Testing module imports..."
python3 -c "
try:
    from database.schema import Base
    print('✅ Database schema: OK')
except Exception as e:
    print(f'❌ Schema import: {e}')
"

echo ""
echo "🎉 DEVELOPMENT SETUP COMPLETE!"
echo ""
echo "📋 NEXT STEPS:"
echo "1. python scripts/create_tables.py"
echo "2. python main.py"
echo ""
echo "🌐 Access points:"
echo "- API: http://localhost:8000"
echo "- Docs: http://localhost:8000/docs"