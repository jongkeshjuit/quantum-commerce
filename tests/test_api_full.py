
import requests
import json
import time
import random

class APITester:
    def __init__(self):
        self.api_url = "http://localhost:8000"
        self.test_email = f"test_{random.randint(1000000000, 9999999999)}@example.com"
        self.token = None
        self.transaction_id = None
        self.passed = 0
        self.failed = 0

    def log_success(self, message):
        print(f"✓ {message}")
        self.passed += 1

    def log_error(self, message):
        print(f"✗ {message}")
        self.failed += 1

    def log_info(self, message):
        print(f"ℹ {message}")

    def test_health_check(self):
        """Test 1: Health Check"""
        self.log_info("Testing health check...")
        try:
            response = requests.get(f"{self.api_url}/")
            if response.status_code == 200:
                self.log_success("Health check passed")
                return True
            else:
                self.log_error(f"Health check failed: {response.status_code}")
                return False
        except Exception as e:
            self.log_error(f"Health check error: {e}")
            return False

    def test_register(self):
        """Test 2: User Registration"""
        self.log_info(f"Registering user: {self.test_email}")
        try:
            response = requests.post(
                f"{self.api_url}/api/auth/register",
                json={
                    "email": self.test_email,
                    "username": "testuser123",
                    "password": "TestPass123!",
                    "full_name": "Test User"
                }
            )
            
            if response.status_code == 200:
                self.log_success("Registration successful")
                return True
            else:
                self.log_error(f"Registration failed: {response.text}")
                return False
        except Exception as e:
            self.log_error(f"Registration error: {e}")
            return False

    def test_login(self):
        """Test 3: User Login"""
        self.log_info("Testing login...")
        try:
            response = requests.post(
                f"{self.api_url}/api/auth/login",
                json={
                    "email": self.test_email,
                    "password": "TestPass123!"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.log_success("Login successful")
                return True
            else:
                self.log_error(f"Login failed: {response.text}")
                return False
        except Exception as e:
            self.log_error(f"Login error: {e}")
            return False

    def test_payment(self):
        """Test 4: Process Payment"""
        self.log_info("Processing payment...")
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.post(
                f"{self.api_url}/api/payments/process",
                headers=headers,
                json={
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
                        {"name": "Test Product", "price": 99.99, "quantity": 1}
                    ]
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                self.transaction_id = data.get("transaction_id")
                self.log_success("Payment processed successfully")
                return True
            else:
                self.log_error(f"Payment failed: {response.text}")
                return False
        except Exception as e:
            self.log_error(f"Payment error: {e}")
            return False

    def test_transactions_list(self):
        """Test 5: List Transactions"""
        self.log_info("Listing transactions...")
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(
                f"{self.api_url}/api/transactions",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                count = len(data.get("transactions", []))
                self.log_success(f"Retrieved {count} transactions")
                return True
            else:
                self.log_error(f"Failed to list transactions: {response.status_code}")
                return False
        except Exception as e:
            self.log_error(f"Transactions list error: {e}")
            return False

    def test_verify_transaction(self):
        """Test 6: Verify Transaction"""
        if not self.transaction_id:
            self.log_info("Skipping verification - no transaction ID")
            return True
            
        self.log_info("Verifying transaction...")
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.post(
                f"{self.api_url}/api/transactions/verify",
                headers=headers,
                json={
                    "transaction_id": self.transaction_id
                }
            )
            
            if response.status_code == 200:
                self.log_success("Transaction verification passed")
                return True
            else:
                self.log_error(f"Transaction verification failed: {response.status_code}")
                return False
        except Exception as e:
            self.log_error(f"Transaction verification error: {e}")
            return False

    def test_crypto_endpoints(self):
        """Test 7: Crypto Endpoints"""
        self.log_info("Testing crypto endpoints...")
        
        # Test IBE params
        try:
            response = requests.get(f"{self.api_url}/api/crypto/ibe/public-params")
            if response.status_code == 200:
                self.log_success("IBE public params retrieved")
            else:
                self.log_error("Failed to get IBE params")
        except Exception as e:
            self.log_error(f"IBE params error: {e}")
        
        # Test merchant keys
        try:
            response = requests.get(f"{self.api_url}/api/crypto/keys/merchant-public")
            if response.status_code == 200:
                self.log_success("Merchant public keys retrieved")
            else:
                self.log_error("Failed to get merchant keys")
        except Exception as e:
            self.log_error(f"Merchant keys error: {e}")
        
        return True

    def test_metrics(self):
        """Test 8: Metrics Endpoint"""
        self.log_info("Testing metrics endpoint...")
        try:
            response = requests.get(f"{self.api_url}/metrics")
            if response.status_code == 200:
                self.log_success("Metrics endpoint working")
                return True
            else:
                self.log_error("Metrics endpoint failed")
                return False
        except Exception as e:
            self.log_error(f"Metrics endpoint error: {e}")
            return False

    def test_admin_protection(self):
        """Test 9: Admin Protection"""
        self.log_info("Testing admin protection...")
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(
                f"{self.api_url}/api/admin/stats",
                headers=headers
            )
            
            if response.status_code == 403:
                self.log_success("Admin protection working correctly")
                return True
            else:
                self.log_error("Admin protection not working")
                return False
        except Exception as e:
            self.log_error(f"Admin test error: {e}")
            return False

    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "="*50)
        print("Quantum-Secure E-Commerce API Test Suite")
        print("="*50)
        print()
        
        tests = [
            ("Test 1: Health Check", self.test_health_check),
            ("Test 2: User Registration", self.test_register),
            ("Test 3: User Login", self.test_login),
            ("Test 4: Process Payment", self.test_payment),
            ("Test 5: List Transactions", self.test_transactions_list),
            ("Test 6: Verify Transaction", self.test_verify_transaction),
            ("Test 7: Crypto Endpoints", self.test_crypto_endpoints),
            ("Test 8: Metrics Endpoint", self.test_metrics),
            ("Test 9: Admin Protection", self.test_admin_protection),
        ]
        
        for name, test_func in tests:
            print(f"\n{name}: {name}")
            test_func()
            time.sleep(0.1)  # Small delay between tests
        
        print("\n" + "="*50)
        print("Test Summary")
        print("="*50)
        print()
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        print(f"Total: {self.passed + self.failed}")
        
        if self.failed == 0:
            print("\n🎉 All tests passed!")
        else:
            print(f"\n⚠️  Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    tester = APITester()
    tester.run_all_tests()