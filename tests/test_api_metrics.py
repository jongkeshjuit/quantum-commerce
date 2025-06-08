#!/usr/bin/env python3
"""
COMPREHENSIVE API METRICS TEST
Test all endpoints và verify metrics
"""
import requests
import time
import json

def test_api_metrics():
    base_url = "http://localhost:8000"
    
    print("🧪 COMPREHENSIVE API METRICS TEST")
    print("=" * 50)
    
    # 1. Wait for API to start
    print("⏳ Waiting for API to start...")
    for i in range(10):
        try:
            r = requests.get(f"{base_url}/", timeout=2)
            if r.status_code == 200:
                print("   ✅ API is ready!")
                break
        except:
            time.sleep(1)
    else:
        print("   ❌ API not responding")
        return False
    
    # 2. Test metrics endpoint
    print("\n📊 Testing metrics endpoint...")
    try:
        r = requests.get(f"{base_url}/metrics", timeout=5)
        if r.status_code == 200:
            metrics_text = r.text
            print(f"   ✅ Metrics endpoint working ({len(metrics_text)} bytes)")
            
            # Check for expected metrics
            expected = ['http_requests_total', 'quantum_signatures_total', 'payments_total']
            for metric in expected:
                if metric in metrics_text:
                    print(f"   ✅ Found metric: {metric}")
                else:
                    print(f"   ⚠️ Missing metric: {metric}")
        else:
            print(f"   ❌ Metrics endpoint failed: {r.status_code}")
    except Exception as e:
        print(f"   ❌ Metrics test error: {e}")
    
    # 3. Generate traffic để tạo metrics
    print("\n🚀 Generating traffic for metrics...")
    
    # Test signing operations
    for i in range(5):
        try:
            transaction = {
                "transaction_id": f"test_tx_{i}",
                "amount": 100 + i * 50,
                "currency": "USD"
            }
            r = requests.post(f"{base_url}/api/crypto/sign", json=transaction, timeout=10)
            if r.status_code == 200:
                print(f"   ✅ Signature {i+1} created")
            else:
                print(f"   ⚠️ Signature {i+1} failed: {r.status_code}")
        except Exception as e:
            print(f"   ❌ Signing error {i+1}: {e}")
    
    # Test payment operations  
    for i in range(3):
        try:
            payment = {
                "amount": 250.50 + i * 100,
                "currency": "USD",
                "payment_method": "card"
            }
            r = requests.post(f"{base_url}/api/payments/process", json=payment, timeout=10)
            if r.status_code == 200:
                data = r.json()
                print(f"   ✅ Payment {i+1}: {data.get('status')} - {data.get('amount')} {data.get('currency')}")
            else:
                print(f"   ⚠️ Payment {i+1} failed: {r.status_code}")
        except Exception as e:
            print(f"   ❌ Payment error {i+1}: {e}")
    
    # Test encryption
    for i in range(2):
        try:
            encrypt_data = {
                "message": f"Secret data {i+1}",
                "identity": f"user{i+1}@quantum.com"
            }
            r = requests.post(f"{base_url}/api/crypto/encrypt", json=encrypt_data, timeout=10)
            if r.status_code == 200:
                print(f"   ✅ Encryption {i+1} completed")
            else:
                print(f"   ⚠️ Encryption {i+1} failed: {r.status_code}")
        except Exception as e:
            print(f"   ❌ Encryption error {i+1}: {e}")
    
    print("\n⏳ Waiting for metrics to update (5 seconds)...")
    time.sleep(5)
    
    # 4. Check updated metrics
    print("\n📈 CHECKING UPDATED METRICS:")
    print("=" * 40)
    
    try:
        r = requests.get(f"{base_url}/metrics", timeout=5)
        if r.status_code == 200:
            metrics_lines = r.text.split('\n')
            
            # Parse metrics
            signature_count = 0
            payment_count = 0
            encryption_count = 0
            request_count = 0
            
            for line in metrics_lines:
                if line.startswith('quantum_signatures_total{') and 'status="success"' in line:
                    signature_count += float(line.split()[-1])
                elif line.startswith('payments_total{') and 'status="success"' in line:
                    payment_count += float(line.split()[-1])
                elif line.startswith('ibe_encryptions_total{') and 'status="success"' in line:
                    encryption_count += float(line.split()[-1])
                elif line.startswith('http_requests_total{'):
                    request_count += float(line.split()[-1])
            
            print(f"🔐 Quantum Signatures: {int(signature_count)}")
            print(f"💳 Payments Processed: {int(payment_count)}")
            print(f"🔒 IBE Encryptions: {int(encryption_count)}")
            print(f"📡 HTTP Requests: {int(request_count)}")
            
            if signature_count > 0 and payment_count > 0:
                print("\n🎉 METRICS TEST SUCCESSFUL!")
                print("✅ All metrics are working properly")
            else:
                print("\n⚠️ Some metrics not updating")
                
        else:
            print(f"❌ Failed to get updated metrics: {r.status_code}")
            
    except Exception as e:
        print(f"❌ Metrics check error: {e}")
    
    # 5. Test Prometheus connection
    print("\n🔍 Testing Prometheus connection...")
    try:
        # Test if Prometheus can scrape our metrics
        r = requests.get("http://localhost:9090/api/v1/targets", timeout=5)
        if r.status_code == 200:
            data = r.json()
            for target in data['data']['activeTargets']:
                if target['labels']['job'] == 'quantum-commerce-api':
                    health = target['health']
                    print(f"   📊 Prometheus target: {health}")
                    if health == 'up':
                        print("   ✅ Prometheus successfully scraping API")
                    else:
                        print(f"   ❌ Prometheus target down: {target.get('lastError', 'Unknown')}")
        else:
            print(f"   ⚠️ Cannot check Prometheus: {r.status_code}")
    except Exception as e:
        print(f"   ⚠️ Prometheus check failed: {e}")
    
    print("\n🎯 QUICK PROMETHEUS QUERIES TO TRY:")
    print("=" * 40)
    print("🔗 http://localhost:9090/graph")
    print("📊 Queries:")
    print("   - quantum_signatures_total")
    print("   - rate(quantum_signatures_total[5m])")
    print("   - payments_total")
    print("   - sum(rate(http_requests_total[5m])) by (status_code)")
    print("   - histogram_quantile(0.95, rate(api_request_duration_seconds_bucket[5m]))")
    
    print("\n🔍 GRAFANA DASHBOARD:")
    print("🔗 http://localhost:3030 (admin/quantum_admin_123)")
    
    return True

if __name__ == "__main__":
    test_api_metrics()
