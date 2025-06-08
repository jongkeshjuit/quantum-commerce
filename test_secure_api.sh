#!/bin/bash
# test_secure_api.sh

API_URL="http://localhost:8000"

echo "🧪 Testing Secure Quantum Commerce API"
echo "======================================"

# 1. Health check
echo "1. Health Check"
curl -s $API_URL/ | jq .

# 2. Register user
echo -e "\n2. Register User"
REGISTER_RESPONSE=$(curl -s -X POST $API_URL/api/auth/register \
    -H "Content-Type: application/json" \
    -d '{
        "email": "test@quantum.com",
        "username": "testuser",
        "password": "Test@123456",
        "full_name": "Test User"
    }')
echo $REGISTER_RESPONSE | jq .

# 3. Login
echo -e "\n3. Login"
LOGIN_RESPONSE=$(curl -s -X POST $API_URL/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{
        "email": "test@quantum.com",
        "password": "Test@123456"
    }')
echo $LOGIN_RESPONSE | jq .

TOKEN=$(echo $LOGIN_RESPONSE | jq -r .access_token)

# 4. Get user info
echo -e "\n4. Get User Info"
curl -s -X GET $API_URL/api/users/me \
    -H "Authorization: Bearer $TOKEN" | jq .

# 5. Test payment
echo -e "\n5. Process Payment"
curl -s -X POST $API_URL/api/payments/process \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "amount": 99.99,
        "currency": "USD",
        "payment_method": "credit_card",
        "payment_data": {
            "card_number": "4111111111111111",
            "exp_month": "12",
            "exp_year": "2025",
            "cvv": "123"
        },
        "items": [
            {"id": "1", "name": "Quantum Laptop", "price": 99.99}
        ]
    }' | jq .

echo -e "\n✅ Tests completed!"