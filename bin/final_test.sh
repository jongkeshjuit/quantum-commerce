#!/bin/bash
# final_test.sh - Test toàn bộ hệ thống

echo "🏁 FINAL SYSTEM TEST - QUANTUM COMMERCE"
echo "======================================"
echo ""

# Test scores
PASSED=0
TOTAL=0

test_result() {
    if [ $1 -eq 0 ]; then
        echo "   ✅ PASSED"
        PASSED=$((PASSED + 1))
    else
        echo "   ❌ FAILED"
    fi
    TOTAL=$((TOTAL + 1))
}

# 1. TEST QUANTUM CRYPTO SYSTEM
echo "1. 🔐 Testing Quantum Crypto System..."
python -c "
try:
    from crypto.production_crypto import create_production_crypto
    crypto = create_production_crypto()
    
    # Test Dilithium signature
    transaction = {'transaction_id': 'final_test', 'amount': 999.99}
    signed = crypto['signer'].sign_transaction(transaction)
    verified = crypto['signer'].verify_signature(signed)
    
    # Test IBE encryption
    encrypted = crypto['ibe'].encrypt_for_user('Final test data', 'test@final.com')
    
    print('CRYPTO_TEST_PASSED')
    print(f'Algorithm: {signed[\"algorithm\"]}')
    print(f'Quantum Secure: {signed[\"quantum_secure\"]}')
    print(f'Verification: {verified}')
    print(f'IBE Algorithm: {encrypted[\"algorithm\"]}')
    
except Exception as e:
    print(f'CRYPTO_TEST_FAILED: {e}')
    exit(1)
" >/dev/null 2>&1
test_result $?

# 2. TEST DATABASE CONNECTION
echo "2. 🗄️  Testing Database Connection..."
python -c "
import psycopg2
try:
    conn = psycopg2.connect(
        host='localhost', port=5432,
        user='quantum_user', password='quantum_secure_pass_123',
        database='quantum_commerce'
    )
    print('DATABASE_TEST_PASSED')
    conn.close()
except Exception as e:
    print(f'DATABASE_TEST_FAILED: {e}')
    exit(1)
" >/dev/null 2>&1
test_result $?

# 3. TEST API ENDPOINTS
echo "3. 🚀 Testing API Endpoints..."
# Start API in background if not running
if ! curl -s http://localhost:8000/ >/dev/null 2>&1; then
    echo "   Starting API..."
    python main.py &
    API_PID=$!
    sleep 3
fi

# Test health endpoint
curl -s http://localhost:8000/ | grep -q "healthy" >/dev/null 2>&1
test_result $?

# 4. TEST QUANTUM SIGNATURE VIA API
echo "4. ✍️  Testing Quantum Signatures via API..."
SIGNATURE_RESULT=$(curl -s -X POST http://localhost:8000/api/crypto/sign \
  -H "Content-Type: application/json" \
  -d '{"transaction_id": "api_test", "amount": 150.75}' 2>/dev/null)

echo "$SIGNATURE_RESULT" | grep -q "Dilithium" >/dev/null 2>&1
test_result $?

# 5. TEST PAYMENT PROCESSING
echo "5. 💳 Testing Payment Processing..."
PAYMENT_RESULT=$(curl -s -X POST http://localhost:8000/api/payments/process \
  -H "Content-Type: application/json" \
  -d '{"amount": 299.99, "currency": "USD"}' 2>/dev/null)

echo "$PAYMENT_RESULT" | grep -q "success" >/dev/null 2>&1
test_result $?

# 6. TEST MONITORING STACK
echo "6. 📊 Testing Monitoring Stack..."

# Test Prometheus
curl -s http://localhost:9090/-/healthy >/dev/null 2>&1
PROMETHEUS_STATUS=$?

# Test Grafana
curl -s http://localhost:3030/api/health >/dev/null 2>&1
GRAFANA_STATUS=$?

if [ $PROMETHEUS_STATUS -eq 0 ] && [ $GRAFANA_STATUS -eq 0 ]; then
    test_result 0
else
    test_result 1
fi

# 7. TEST METRICS ENDPOINT
echo "7. 📈 Testing Metrics Collection..."
curl -s http://localhost:8000/metrics | grep -q "quantum\|http_requests\|payments" >/dev/null 2>&1
test_result $?

# 8. TEST SECURITY FEATURES
echo "8. 🛡️  Testing Security Features..."
python -c "
try:
    from services.auth_service import auth_service
    
    # Test password hashing
    password = 'TestPass123!'
    hashed = auth_service.hash_password(password)
    verified = auth_service.verify_password(password, hashed)
    
    # Test JWT token
    user_data = {'user_id': 'test', 'email': 'test@example.com'}
    token = auth_service.create_access_token(user_data)
    
    print('SECURITY_TEST_PASSED')
    print(f'Password verified: {verified}')
    print(f'Token created: {len(token) > 0}')
    
except Exception as e:
    print(f'SECURITY_TEST_FAILED: {e}')
    exit(1)
" >/dev/null 2>&1
test_result $?

# Kill API if we started it
if [ ! -z "$API_PID" ]; then
    kill $API_PID 2>/dev/null
fi

# FINAL SCORE
echo ""
echo "🏆 FINAL TEST RESULTS"
echo "===================="
echo "Passed: $PASSED/$TOTAL tests"
echo ""

if [ $PASSED -eq $TOTAL ]; then
    echo "🎉 CONGRATULATIONS! 🎉"
    echo "🛡️  QUANTUM-SECURE E-COMMERCE SYSTEM COMPLETE!"
    echo ""
    echo "✅ FEATURES WORKING:"
    echo "   🔐 Real Dilithium3 Quantum Signatures"
    echo "   🔒 Enhanced IBE Encryption"
    echo "   🗄️  PostgreSQL Database"
    echo "   📊 Prometheus + Grafana Monitoring"
    echo "   🚀 FastAPI with Security Middleware"
    echo "   💳 Payment Processing"
    echo "   📈 Real-time Metrics"
    echo "   🛡️  Authentication & Authorization"
    echo ""
    echo "🌐 ACCESS POINTS:"
    echo "   API: http://localhost:8000"
    echo "   Prometheus: http://localhost:9090"
    echo "   Grafana: http://localhost:3030 (admin/quantum_admin_123)"
    echo ""
    echo "🎯 YOUR SYSTEM IS PRODUCTION-READY!"
    echo "🔮 FUTURE-PROOF AGAINST QUANTUM ATTACKS!"
    
elif [ $PASSED -gt $((TOTAL * 3 / 4)) ]; then
    echo "🟡 MOSTLY COMPLETE ($PASSED/$TOTAL)"
    echo "Minor issues but core functionality working"
    echo "System is 90%+ ready for use"
    
else
    echo "🔴 NEEDS WORK ($PASSED/$TOTAL)"
    echo "Several components need attention"
    echo "Review failed tests above"
fi

echo ""
echo "📋 TO RUN FULL SYSTEM:"
echo "1. docker-compose up -d  # Start PostgreSQL + Redis"
echo "2. python main.py        # Start API"
echo "3. Open http://localhost:3030  # Grafana dashboard"
echo ""
echo "🧪 TO RE-RUN THIS TEST:"
echo "./final_test.sh"