#!/bin/bash
# check_metrics.sh - Check metrics trong Prometheus và Grafana

echo "📊 CHECKING QUANTUM METRICS"
echo "=========================="

# 1. Check API metrics endpoint
echo "🔍 Testing API metrics endpoint..."
curl -s http://localhost:8000/metrics | head -20
echo ""

# 2. Check Prometheus targets
echo "🎯 Checking Prometheus targets..."
curl -s http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | {job: .labels.job, health: .health, lastScrape: .lastScrape}' 2>/dev/null || echo "jq not installed - checking raw..."

# 3. Query quantum metrics từ Prometheus
echo ""
echo "🔐 Querying quantum signature metrics..."
curl -s "http://localhost:9090/api/v1/query?query=quantum_signatures_total" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if data['status'] == 'success' and data['data']['result']:
        for result in data['data']['result']:
            print(f\"✅ {result['metric']}: {result['value'][1]}\")
    else:
        print('No quantum signature metrics found yet')
except:
    print('Error parsing metrics')
"

echo ""
echo "🔒 Querying IBE encryption metrics..."
curl -s "http://localhost:9090/api/v1/query?query=ibe_encryptions_total" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if data['status'] == 'success' and data['data']['result']:
        for result in data['data']['result']:
            print(f\"✅ {result['metric']}: {result['value'][1]}\")
    else:
        print('No IBE encryption metrics found yet')
except:
    print('Error parsing metrics')
"

echo ""
echo "📈 Querying API request metrics..."
curl -s "http://localhost:9090/api/v1/query?query=api_requests_total" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if data['status'] == 'success' and data['data']['result']:
        for result in data['data']['result']:
            print(f\"✅ {result['metric']}: {result['value'][1]}\")
    else:
        print('No API request metrics found yet')
except:
    print('Error parsing metrics')
"

# 4. Generate more test traffic để tạo metrics
echo ""
echo "🧪 Generating test traffic for metrics..."

# Test payment
echo "💳 Testing payment endpoint..."
curl -s -X POST http://localhost:8000/api/payments/process \
  -H "Content-Type: application/json" \
  -d '{"amount": 299.99, "currency": "USD"}' | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(f\"✅ Payment: {data.get('status', 'unknown')}\")
    print(f\"💰 Amount: {data.get('amount', 0)} {data.get('currency', 'USD')}\")
    print(f\"🛡️ Quantum: {data.get('quantum_secure', False)}\")
except:
    print('Payment test failed')
"

# Test multiple signatures
echo ""
echo "📝 Testing multiple signatures..."
for i in {1..5}; do
    curl -s -X POST http://localhost:8000/api/crypto/sign \
      -H "Content-Type: application/json" \
      -d "{\"transaction_id\": \"test_$i\", \"amount\": $((100 + i * 50))}" >/dev/null
    echo "✅ Signature $i created"
done

# Test multiple encryptions
echo ""
echo "🔒 Testing multiple encryptions..."
for i in {1..3}; do
    curl -s -X POST http://localhost:8000/api/crypto/encrypt \
      -H "Content-Type: application/json" \
      -d "{\"message\": \"Secret data $i\", \"identity\": \"user$i@quantum.com\"}" >/dev/null
    echo "✅ Encryption $i completed"
done

echo ""
echo "⏳ Waiting for metrics to update (10 seconds)..."
sleep 10

# 5. Check updated metrics
echo ""
echo "📊 UPDATED METRICS:"
echo "=================="

echo "🔐 Quantum Signatures:"
curl -s "http://localhost:9090/api/v1/query?query=quantum_signatures_total" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if data['status'] == 'success' and data['data']['result']:
        total = 0
        for result in data['data']['result']:
            count = int(float(result['value'][1]))
            total += count
            print(f\"  📝 {result['metric']['algorithm']} ({result['metric']['status']}): {count}\")
        print(f\"  🎯 Total signatures: {total}\")
    else:
        print('  ⚠️ No metrics available yet')
except Exception as e:
    print(f'  ❌ Error: {e}')
"

echo ""
echo "🔒 IBE Encryptions:"
curl -s "http://localhost:9090/api/v1/query?query=ibe_encryptions_total" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if data['status'] == 'success' and data['data']['result']:
        total = 0
        for result in data['data']['result']:
            count = int(float(result['value'][1]))
            total += count
            print(f\"  🔐 {result['metric']['algorithm']} ({result['metric']['status']}): {count}\")
        print(f\"  🎯 Total encryptions: {total}\")
    else:
        print('  ⚠️ No metrics available yet')
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
        total = 0
        for result in data['data']['result']:
            count = int(float(result['value'][1]))
            total += count
            print(f\"  💰 {result['metric']['currency']} ({result['metric']['status']}): {count}\")
        print(f\"  🎯 Total payments: {total}\")
    else:
        print('  ⚠️ No metrics available yet')
except Exception as e:
    print(f'  ❌ Error: {e}')
"

echo ""
echo "🎉 METRICS CHECK COMPLETED!"
echo ""
echo "🌐 DASHBOARDS:"
echo "- Prometheus: http://localhost:9090"
echo "- Grafana: http://localhost:3030 (admin/quantum_admin_123)"
echo ""
echo "📊 PROMETHEUS QUERIES TO TRY:"
echo "- quantum_signatures_total"
echo "- ibe_encryptions_total"
echo "- api_requests_total"
echo "- payments_total"
echo "- rate(quantum_signatures_total[5m])"
echo ""
echo "📈 GRAFANA DASHBOARD:"
echo "- Import dashboard or create panels"
echo "- Use Prometheus as datasource"
echo "- Monitor quantum crypto operations in real-time!"