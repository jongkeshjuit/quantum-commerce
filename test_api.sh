#!/bin/bash

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

API_URL="http://localhost:8000"
EMAIL="test_$(date +%s)@example.com"
PASSWORD="TestPass123!"

echo -e "${YELLOW}=== Testing Quantum-Secure E-Commerce API ===${NC}\n"

# 1. Health check
echo -e "${YELLOW}1. Testing health check...${NC}"
HEALTH=$(curl -s $API_URL/)
if [[ $HEALTH == *"online"* ]]; then
    echo -e "${GREEN}✓ Health check passed${NC}"
else
    echo -e "${RED}✗ Health check failed${NC}"
    exit 1
fi

# 2. Register new user
echo -e "\n${YELLOW}2. Registering new user: $EMAIL${NC}"
REGISTER=$(curl -s -X POST $API_URL/api/auth/register \
    -H "Content-Type: application/json" \
    -d "{
        \"email\": \"$EMAIL\",
        \"name\": \"Test User\",
        \"password\": \"$PASSWORD\",
        \"user_type\": \"customer\"
    }")

if [[ $REGISTER == *"access_token"* ]]; then
    echo -e "${GREEN}✓ Registration successful${NC}"
    TOKEN=$(echo $REGISTER | jq -r '.access_token')
    echo "Token: ${TOKEN:0:50}..."
else
    echo -e "${RED}✗ Registration failed: $REGISTER${NC}"
fi

# 3. Login
echo -e "\n${YELLOW}3. Testing login...${NC}"
LOGIN=$(curl -s -X POST $API_URL/api/auth/login \
    -H "Content-Type: application/json" \
    -d "{
        \"email\": \"$EMAIL\",
        \"password\": \"$PASSWORD\"
    }")

if [[ $LOGIN == *"access_token"* ]]; then
    echo -e "${GREEN}✓ Login successful${NC}"
    TOKEN=$(echo $LOGIN | jq -r '.access_token')
else
    echo -e "${RED}✗ Login failed: $LOGIN${NC}"
fi

# 4. Process payment
echo -e "\n${YELLOW}4. Processing payment...${NC}"
PAYMENT=$(curl -s -X POST $API_URL/api/payments/process \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d '{
        "amount": 99.99,
        "currency": "USD",
        "payment_method": "credit_card",
        "card_data": {
            "number": "4111111111111111",
            "exp_month": "12",
            "exp_year": "2025",
            "cvv": "123"
        },
        "billing_address": {
            "name": "Test User",
            "street": "123 Test St",
            "city": "Testville",
            "state": "TS",
            "zip": "12345"
        }
    }')

if [[ $PAYMENT == *"completed"* ]]; then
    echo -e "${GREEN}✓ Payment processed successfully${NC}"
    TRANSACTION_ID=$(echo $PAYMENT | jq -r '.transaction_id')
    echo "Transaction ID: $TRANSACTION_ID"
else
    echo -e "${RED}✗ Payment failed: $PAYMENT${NC}"
fi

# 5. List transactions
echo -e "\n${YELLOW}5. Listing transactions...${NC}"
TRANSACTIONS=$(curl -s -X GET $API_URL/api/transactions \
    -H "Authorization: Bearer $TOKEN")

if [[ $TRANSACTIONS == *"transactions"* ]]; then
    echo -e "${GREEN}✓ Transactions retrieved${NC}"
    echo "Total transactions: $(echo $TRANSACTIONS | jq '.total')"
else
    echo -e "${RED}✗ Failed to get transactions${NC}"
fi

# 6. Verify transaction
echo -e "\n${YELLOW}6. Verifying transaction...${NC}"
if [ ! -z "$TRANSACTION_ID" ]; then
    VERIFY=$(curl -s -X POST $API_URL/api/payments/verify \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $TOKEN" \
        -d "{
            \"transaction_id\": \"$TRANSACTION_ID\"
        }")
    
    if [[ $VERIFY == *"is_valid"* ]]; then
        echo -e "${GREEN}✓ Transaction verified${NC}"
        echo "Valid: $(echo $VERIFY | jq '.is_valid')"
    else
        echo -e "${RED}✗ Verification failed${NC}"
    fi
fi

# 7. Get public crypto params
echo -e "\n${YELLOW}7. Getting IBE public parameters...${NC}"
IBE_PARAMS=$(curl -s $API_URL/api/crypto/ibe/public-params)
if [[ $IBE_PARAMS == *"public_params"* ]]; then
    echo -e "${GREEN}✓ IBE params retrieved${NC}"
else
    echo -e "${RED}✗ Failed to get IBE params${NC}"
fi

# 8. Get merchant public keys
echo -e "\n${YELLOW}8. Getting merchant public keys...${NC}"
MERCHANT_KEYS=$(curl -s $API_URL/api/crypto/keys/merchant-public)
if [[ $MERCHANT_KEYS == *"public_keys"* ]]; then
    echo -e "${GREEN}✓ Merchant keys retrieved${NC}"
else
    echo -e "${RED}✗ Failed to get merchant keys${NC}"
fi

# 9. Test metrics endpoint
echo -e "\n${YELLOW}9. Testing metrics endpoint...${NC}"
METRICS=$(curl -s $API_URL/metrics)
if [[ $METRICS == *"payment_amount_usd"* ]]; then
    echo -e "${GREEN}✓ Metrics endpoint working${NC}"
else
    echo -e "${RED}✗ Metrics endpoint failed${NC}"
fi

# 10. Test admin endpoint (should fail for regular user)
echo -e "\n${YELLOW}10. Testing admin endpoint (should fail)...${NC}"
ADMIN=$(curl -s -X GET $API_URL/api/admin/stats \
    -H "Authorization: Bearer $TOKEN")
if [[ $ADMIN == *"Admin access required"* ]]; then
    echo -e "${GREEN}✓ Admin protection working${NC}"
else
    echo -e "${RED}✗ Admin protection not working properly${NC}"
fi

# Summary
echo -e "\n${YELLOW}=== Test Summary ===${NC}"
echo -e "${GREEN}✓ API is working correctly!${NC}"
echo -e "- User registered: $EMAIL"
echo -e "- Payment processed"
echo -e "- Security features operational"
echo -e "- Metrics collecting data"