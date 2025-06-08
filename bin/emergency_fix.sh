#!/bin/bash
# emergency_fix.sh - Sửa monitoring ngay lập tức

echo "🚨 EMERGENCY FIX FOR MONITORING"
echo "==============================="

# 1. Kill process đang chiếm port 8000
echo "🔍 Finding process using port 8000..."
PORT_PID=$(lsof -ti:8000 2>/dev/null)
if [ ! -z "$PORT_PID" ]; then
    echo "🔫 Killing process $PORT_PID using port 8000..."
    kill -9 $PORT_PID
    sleep 2
else
    echo "ℹ️ No process found on port 8000"
fi

# 2. Stop tất cả containers và clean up
echo "🛑 Stopping and cleaning up containers..."
docker-compose down --remove-orphans
docker container prune -f

# 3. Fix Prometheus config để match container names thực tế
echo "📝 Fixing Prometheus config for actual container names..."
cat > monitoring/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  # Prometheus self-monitoring
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  # API - Use actual container name from docker ps
  - job_name: 'quantum-commerce-api'
    static_configs:
      - targets: ['qc_api:8000']  # ✅ Match actual container name
    scrape_interval: 10s
    metrics_path: '/metrics'
    scheme: 'http'
    scrape_timeout: 10s
EOF

# 4. Start lại containers theo đúng thứ tự
echo "🚀 Starting containers in correct order..."

# Start infrastructure first
echo "  🗄️ Starting database and cache..."
docker-compose up -d postgres redis vault

# Wait for DB to be ready
echo "  ⏳ Waiting for database..."
sleep 10

# Start API
echo "  🔧 Starting API..."
docker-compose up -d api

# Wait for API to be ready
echo "  ⏳ Waiting for API to start..."
sleep 15

# Check API status
echo "🔍 Checking API status..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ API is running!"
    
    # Start monitoring
    echo "  📊 Starting monitoring..."
    docker-compose up -d prometheus grafana
    
    # Wait for Prometheus
    sleep 10
    
    echo "🎯 Checking containers..."
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    
    echo ""
    echo "🔍 Testing connectivity..."
    
    # Test API from host
    if curl -s http://localhost:8000/health > /dev/null; then
        echo "✅ API reachable from host"
    else
        echo "❌ API not reachable from host"
    fi
    
    # Get actual container name for API
    API_CONTAINER=$(docker ps --format "{{.Names}}" | grep -E "(api|qc_api)" | head -1)
    echo "🐳 API container name: $API_CONTAINER"
    
    # Test API from Prometheus container
    if docker exec qsc_prometheus wget -qO- http://$API_CONTAINER:8000/health > /dev/null 2>&1; then
        echo "✅ API reachable from Prometheus"
    else
        echo "❌ API not reachable from Prometheus"
        echo "🔧 Fixing Prometheus config with correct container name..."
        
        # Update Prometheus config with actual container name
        docker exec qsc_prometheus sh -c "
            sed -i 's/qc_api:8000/$API_CONTAINER:8000/g' /etc/prometheus/prometheus.yml
        " 2>/dev/null || echo "Could not update config inside container"
        
        # Restart Prometheus to reload config
        docker-compose restart prometheus
        sleep 5
    fi
    
    # Generate some test traffic
    echo ""
    echo "🧪 Generating test traffic..."
    for i in {1..3}; do
        curl -s -X POST http://localhost:8000/api/crypto/sign \
          -H "Content-Type: application/json" \
          -d "{\"transaction_id\": \"fix_test_$i\", \"amount\": $((100 + i * 25))}" > /dev/null
        echo "  ✅ Test signature $i created"
    done
    
    # Wait and check metrics
    echo ""
    echo "⏳ Waiting for metrics to be collected..."
    sleep 20
    
    echo "📊 Checking Prometheus targets:"
    curl -s http://localhost:9090/api/v1/targets | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    for target in data['data']['activeTargets']:
        job = target['labels']['job']
        health = target['health']
        url = target['scrapeUrl']
        icon = '✅' if health == 'up' else '❌'
        print(f'  {icon} {job}: {health} ({url})')
except Exception as e:
    print(f'Error: {e}')
"
    
    echo ""
    echo "🎉 EMERGENCY FIX COMPLETED!"
    echo ""
    echo "🌐 DASHBOARDS:"
    echo "- Prometheus: http://localhost:9090"
    echo "- Grafana: http://localhost:3030 (admin/quantum_admin_123)"
    echo "- API: http://localhost:8000/health"
    echo ""
    
else
    echo "❌ API failed to start. Checking logs..."
    docker logs qc_api 2>/dev/null || docker logs $(docker ps -q --filter "name=api") 2>/dev/null || echo "No API container found"
    
    echo ""
    echo "🔧 MANUAL DEBUG STEPS:"
    echo "1. Check if port 8000 is still busy:"
    echo "   lsof -i:8000"
    echo ""
    echo "2. Try starting API manually:"
    echo "   docker-compose up api"
    echo ""
    echo "3. Check docker-compose.yml for correct service names"
    
fi