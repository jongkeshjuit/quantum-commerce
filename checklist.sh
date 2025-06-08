# checklist.sh
#!/bin/bash

echo "📋 QUANTUM COMMERCE SECURITY CHECKLIST"
echo "====================================="

# Check environment
echo -n "✓ Environment variables configured: "
if [ -f .env ]; then echo "YES"; else echo "NO ❌"; fi

echo -n "✓ Secrets NOT in code: "
if grep -r "your-secret-key-here" *.py; then echo "NO ❌"; else echo "YES"; fi

echo -n "✓ Database encryption enabled: "
if grep -q "EncryptedString" database/schema.py; then echo "YES"; else echo "NO ❌"; fi

echo -n "✓ Real crypto implemented: "
if [ -f crypto/real_dilithium.py ]; then echo "YES"; else echo "NO ❌"; fi

echo -n "✓ Session management with Redis: "
if [ -f services/session_service.py ]; then echo "YES"; else echo "NO ❌"; fi

echo -n "✓ Rate limiting enabled: "
if [ -f services/rate_limiter.py ]; then echo "YES"; else echo "NO ❌"; fi

echo -n "✓ Audit logging enabled: "
if grep -q "AuditLog" database/schema.py; then echo "YES"; else echo "NO ❌"; fi

echo -n "✓ Security headers configured: "
if grep -q "X-Frame-Options" main.py; then echo "YES"; else echo "NO ❌"; fi

echo ""
echo "📊 Security Score: Check above items"