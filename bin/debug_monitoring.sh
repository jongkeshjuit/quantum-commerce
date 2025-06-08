#!/bin/bash
# debug_monitoring.sh - Debug monitoring issues

echo "🔍 DEBUGGING MONITORING SETUP"
echo "=============================="

# 1. Check if containers are running
echo "📋 Container Status:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "🌐 Network Information:"
docker network ls
docker network inspect quantum-secure-commerce_quantum-network 2>/dev/null | jq '.[0].Containers' 2>/dev/null || echo "Network info not available"

echo ""
echo "🔍 Testing API endpoint directly:"
if curl -s http://localhost:8000/health; then
    echo "✅ API reachable from host"
else
    echo "❌ API not reachable from host"
fi

echo ""
echo "📊 Testing metrics endpoint:"
if curl -s http://localhost:8000/metrics | head -3; then
    echo "✅ Metrics endpoint working"
else
    echo "❌ Metrics endpoint not working"
fi

echo ""
echo "🐳 Testing from inside Prometheus container:"
docker exec qsc_prometheus wget -qO- http://qsc_api:8000/health 2>/dev/null && echo "✅ API reachable from Prometheus" || echo "❌ API not reachable from Prometheus"

echo ""
echo "🎯 Prometheus config check:"
docker exec qsc_prometheus cat /etc/prometheus/prometheus.yml | grep -A 5 "quantum-commerce-api"

echo ""
echo "📈 Prometheus targets API:"
curl -s http://localhost:9090/api/v1/targets | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print('Target Status:')
    for target in data['data']['activeTargets']:
        print(f'  Job: {target[\"labels\"][\"job\"]}')
        print(f'  Health: {target[\"health\"]}')
        print(f'  URL: {target[\"scrapeUrl\"]}')
        print(f'  Last Error: {target.get(\"lastError\", \"none\")}')
        print('  ---')
except:
    print('Could not parse targets')
"

echo ""
echo "🔧 QUICK FIXES:"
echo "1. If API not reachable from Prometheus:"
echo "   docker-compose restart prometheus"
echo ""
echo "2. If containers on different networks:"
echo "   docker-compose down && docker-compose up -d"
echo ""
echo "3. If metrics still not working:"
echo "   Check main.py has: app.add_middleware(prometheus_middleware)"
echo ""
echo "4. Check logs:"
echo "   docker logs qsc_api"
echo "   docker logs qsc_prometheus"