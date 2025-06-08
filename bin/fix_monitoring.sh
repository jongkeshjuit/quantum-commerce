#!/bin/bash
# fix_monitoring.sh - Sửa và restart monitoring stack

echo "🔧 FIXING PROMETHEUS & GRAFANA CONFIGURATION"
echo "============================================="

# 1. Stop các containers
echo "🛑 Stopping containers..."
docker-compose down prometheus grafana

# 2. Tạo lại prometheus config
echo "📝 Creating new prometheus config..."
mkdir -p monitoring

cat > monitoring/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  # Prometheus self-monitoring
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  # Quantum Commerce API
  - job_name: 'quantum-commerce-api'
    static_configs:
      - targets: ['qsc_api:8000']  # ✅ Sử dụng container name
    scrape_interval: 10s
    metrics_path: '/metrics'
    scheme: 'http'
    scrape_timeout: 10s

  # Node Exporter for system metrics
  - job_name: 'node_exporter'
    static_configs:
      - targets: ['node_exporter:9100']
    scrape_interval: 30s
EOF

# 3. Tạo Grafana datasource config
echo "📊 Creating Grafana datasource..."
mkdir -p monitoring/grafana/datasources

cat > monitoring/grafana/datasources/prometheus.yml << 'EOF'
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true
EOF

# 4. Tạo Grafana dashboard config
mkdir -p monitoring/grafana/dashboards

cat > monitoring/grafana/dashboards/dashboard.yml << 'EOF'
apiVersion: 1

providers:
  - name: 'default'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /etc/grafana/provisioning/dashboards
EOF

# 5. Restart containers với fixed config
echo "🚀 Restarting containers with fixed config..."
docker-compose up -d

# 6. Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 15

# 7. Check container status
echo ""
echo "📋 CONTAINER STATUS:"
echo "==================="
docker-compose ps

# 8. Test API metrics endpoint
echo ""
echo "🔍 Testing API metrics endpoint..."
if curl -s http://localhost:8000/metrics | head -5; then
    echo "✅ API metrics endpoint working"
else
    echo "❌ API metrics endpoint not responding"
fi

# 9. Test Prometheus targets
echo ""
echo "🎯 Checking Prometheus targets..."
sleep 5  # Give Prometheus time to scrape

curl -s http://localhost:9090/api/v1/targets 2>/dev/null | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print('Prometheus Targets Status:')
    for target in data['data']['activeTargets']:
        job = target['labels']['job']
        health = target['health']
        endpoint = target['scrapeUrl']
        icon = '✅' if health == 'up' else '❌'
        print(f'  {icon} {job}: {health} ({endpoint})')
except Exception as e:
    print(f'Error checking targets: {e}')
    print('Checking manually...')
    import subprocess
    result = subprocess.run(['curl', '-s', 'http://localhost:9090/api/v1/targets'], capture_output=True, text=True)
    print('Raw response:', result.stdout[:200])
"

# 10. Generate test traffic
echo ""
echo "🧪 Generating test traffic..."
for i in {1..3}; do
    echo "📝 Creating signature $i..."
    curl -s -X POST http://localhost:8000/api/crypto/sign \
      -H "Content-Type: application/json" \
      -d "{\"transaction_id\": \"test_$i\", \"amount\": $((100 + i * 50))}" > /dev/null
    
    echo "💳 Processing payment $i..."
    curl -s -X POST http://localhost:8000/api/payments/process \
      -H "Content-Type: application/json" \
      -d "{\"amount\": $((100 + i * 50)).99, \"currency\": \"USD\"}" > /dev/null
done

echo ""
echo "⏳ Waiting for metrics to be scraped..."
sleep 20

# 11. Check metrics in Prometheus
echo ""
echo "📊 CHECKING METRICS IN PROMETHEUS:"
echo "=================================="

echo "🔐 Quantum Signatures:"
curl -s "http://localhost:9090/api/v1/query?query=quantum_signatures_total" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if data['status'] == 'success' and data['data']['result']:
        for result in data['data']['result']:
            metric = result['metric']
            value = result['value'][1]
            print(f'  ✅ {metric.get(\"algorithm\", \"unknown\")} ({metric.get(\"status\", \"unknown\")}): {value}')
    else:
        print('  ⚠️ No quantum signature metrics found yet')
except Exception as e:
    print(f'  ❌ Error: {e}')
"

echo ""
echo "💳 Payments:"
curl -s "http://localhost:9090/api/v1/query?query=payments_total" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if data['status'] == 'success' and data['data']['result']:
        for result in data['data']['result']:
            metric = result['metric']
            value = result['value'][1]
            print(f'  ✅ {metric.get(\"currency\", \"unknown\")} ({metric.get(\"status\", \"unknown\")}): {value}')
    else:
        print('  ⚠️ No payment metrics found yet')
except Exception as e:
    print(f'  ❌ Error: {e}')
"

echo ""
echo "📈 API Requests:"
curl -s "http://localhost:9090/api/v1/query?query=api_requests_total" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if data['status'] == 'success' and data['data']['result']:
        total = 0
        for result in data['data']['result']:
            value = int(float(result['value'][1]))
            total += value
        print(f'  ✅ Total API requests: {total}')
        if total == 0:
            print('  ⚠️ No API requests tracked yet - metrics may need more time')
    else:
        print('  ⚠️ No API request metrics found yet')
except Exception as e:
    print(f'  ❌ Error: {e}')
"

echo ""
echo "🎉 MONITORING SETUP COMPLETED!"
echo ""
echo "🌐 ACCESS DASHBOARDS:"
echo "- Prometheus: http://localhost:9090"
echo "- Grafana: http://localhost:3030 (admin/quantum_admin_123)"
echo "- API Health: http://localhost:8000/health"
echo "- API Metrics: http://localhost:8000/metrics"
echo ""
echo "📊 USEFUL PROMETHEUS QUERIES:"
echo "- quantum_signatures_total"
echo "- payments_total"
echo "- rate(quantum_signatures_total[5m])"
echo "- increase(payments_total[1h])"
echo ""
echo "💡 TIP: Nếu metrics vẫn không hiện, đợi 1-2 phút để Prometheus scrape data"