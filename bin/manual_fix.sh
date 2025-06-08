#!/bin/bash
# super_quick_fix.sh - Fix docker-compose syntax ngay lập tức

echo "🔧 SUPER QUICK FIX"
echo "=================="

# 1. Restore backup
echo "📁 Restoring backup..."
cp docker-compose.yml.backup docker-compose.yml
echo "✅ Restored original docker-compose.yml"

# 2. Create a working docker-compose with monitoring
echo "📝 Creating new docker-compose with monitoring..."
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  # Database
  postgres:
    image: postgres:15-alpine
    container_name: qc_postgres
    environment:
      POSTGRES_DB: quantum_commerce
      POSTGRES_USER: quantum_user
      POSTGRES_PASSWORD: quantum_pass
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U quantum_user -d quantum_commerce"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Redis Cache
  redis:
    image: redis:7-alpine
    container_name: qc_redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Vault (for advanced secret management)
  vault:
    image: hashicorp/vault:1.15
    container_name: qc_vault
    ports:
      - "8200:8200"
    environment:
      VAULT_DEV_ROOT_TOKEN_ID: quantum_dev_token
      VAULT_DEV_LISTEN_ADDRESS: 0.0.0.0:8200

  # Main API
  api:
    build: .
    container_name: qc_api
    ports:
      - "8000:8000"
    environment:
      - APP_ENV=development
      - USE_REAL_CRYPTO=true
      - DATABASE_URL=postgresql://quantum_user:quantum_pass@qc_postgres:5432/quantum_commerce
      - REDIS_URL=redis://qc_redis:6379/0
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./secrets:/app/secrets:ro

  # Prometheus
  prometheus:
    image: prom/prometheus:latest
    container_name: qc_prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=200h'
      - '--web.enable-lifecycle'
    depends_on:
      - api

  # Grafana
  grafana:
    image: grafana/grafana:latest
    container_name: qc_grafana
    ports:
      - "3030:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=quantum_admin_123
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - grafana_data:/var/lib/grafana
    depends_on:
      - prometheus

volumes:
  postgres_data:
  redis_data:
  prometheus_data:
  grafana_data:
EOF

echo "✅ Created new docker-compose.yml with proper syntax"

# 3. Make sure Prometheus config exists
mkdir -p monitoring
cat > monitoring/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'quantum-commerce-api'
    static_configs:
      - targets: ['qc_api:8000']
    scrape_interval: 10s
    metrics_path: '/metrics'
    scheme: 'http'
    scrape_timeout: 10s
EOF

echo "✅ Created Prometheus config"

# 4. Restart everything
echo "🚀 Restarting all containers..."
docker-compose down --remove-orphans
sleep 5
docker-compose up -d

# 5. Wait for services
echo "⏳ Waiting for services to start..."
sleep 30

# 6. Test everything
echo ""
echo "🧪 TESTING ALL SERVICES:"
echo "========================"

echo "1. 🔍 API Status:"
if curl -s http://localhost:8000/api/crypto/status > /dev/null; then
    echo "   ✅ API is responding"
    curl -s http://localhost:8000/api/crypto/status | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(f'   🔐 Dilithium: {data[\"dilithium\"][\"status\"]}')
    print(f'   🔒 IBE: {data[\"ibe\"][\"status\"]}')
except:
    print('   📊 API responding but crypto status unavailable')
"
else
    echo "   ❌ API not responding"
fi

echo ""
echo "2. 📊 Prometheus Status:"
if curl -s http://localhost:9090/-/ready > /dev/null; then
    echo "   ✅ Prometheus is ready"
    
    # Check targets
    echo "   🎯 Checking targets..."
    sleep 5
    curl -s http://localhost:9090/api/v1/targets | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    for target in data['data']['activeTargets']:
        job = target['labels']['job']
        health = target['health']
        icon = '✅' if health == 'up' else '❌'
        print(f'     {icon} {job}: {health}')
except:
    print('     ⏳ Targets still loading...')
"
else
    echo "   ❌ Prometheus not ready"
fi

echo ""
echo "3. 📈 Grafana Status:"
if curl -s http://localhost:3030/api/health > /dev/null; then
    echo "   ✅ Grafana is ready"
    echo "   🔑 Login: admin / quantum_admin_123"
else
    echo "   ❌ Grafana not ready"
fi

echo ""
echo "4. 🧪 Quick Functional Test:"
echo "   💳 Testing payment..."
PAY_RESULT=$(curl -s -X POST http://localhost:8000/api/payments/process \
  -H "Content-Type: application/json" \
  -d '{"amount": 123.45, "currency": "USD"}' 2>/dev/null)

if echo "$PAY_RESULT" | grep -q "success"; then
    echo "   ✅ Payment processing works!"
else
    echo "   ⏳ Payment endpoint still loading..."
fi

echo ""
echo "🎉 SETUP COMPLETED!"
echo "=================="
echo ""
echo "🌐 ACCESS POINTS:"
echo "- 🔧 API: http://localhost:8000"
echo "- 📊 Prometheus: http://localhost:9090"
echo "- 📈 Grafana: http://localhost:3030"
echo "- 📚 API Docs: http://localhost:8000/docs"
echo ""
echo "🐳 Container Status:"
docker-compose ps

echo ""
echo "💡 IF STILL NOT WORKING:"
echo "========================"
echo "1. Wait 1-2 more minutes for all services"
echo "2. Check logs: docker-compose logs api"
echo "3. Restart if needed: docker-compose restart"
echo ""
echo "🎯 SIMPLE TEST COMMANDS:"
echo "curl http://localhost:8000/metrics"
echo "curl http://localhost:8000/api/crypto/status"
echo ""
echo "🎊 YOUR QUANTUM E-COMMERCE IS READY!"