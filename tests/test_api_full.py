#!/usr/bin/env python3
"""
Comprehensive API testing script
"""

import requests
import json
import time
from datetime import datetime
from colorama import init, Fore, Style

init(autoreset=True)

API_URL = "http://localhost:8000"

class APITester:
    def __init__(self):
        self.api_url = API_URL
        self.token = None
        self.user_email = f"test_{int(time.time())}@example.com"
        self.user_password = "TestPass123!"
        self.transaction_id = None
        self.test_results = []
        
    def log_success(self, message):
        print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")
        self.test_results.append(("PASS", message))
        
    def log_error(self, message):
        print(f"{Fore.RED}✗ {message}{Style.RESET_ALL}")
        self.test_results.append(("FAIL", message))
        
    def log_info(self, message):
        print(f"{Fore.YELLOW}ℹ {message}{Style.RESET_ALL}")
        
    def test_health_check(self):
        """Test 1: Health Check"""
        self.log_info("Testing health check...")
        try:
            response = requests.get(f"{self.api_url}/")
            data = response.json()
            
            if response.status_code == 200 and data.get("status") == "online":
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
        self.log_info(f"Registering user: {self.user_email}")
        try:
            response = requests.post(
                f"{self.api_url}/api/auth/register",
                json={
                    "email": self.user_email,
                    "name": "Test User",
                    "password": self.user_password,
                    "user_type": "customer"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.log_success(f"Registration successful, token: {self.token[:30]}...")
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
                    "email": self.user_email,
                    "password": self.user_password
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
                    "card_data": {
                        "number": "4111111111111111",
                        "exp_month": "12",
                        "exp_year": "2025",
                        "cvv": "123"
                    },
                    "billing_address": {
                        "name": "Test User",
                        "street": "123 Test St",
                        "city": "Test City",
                        "state": "TS",
                        "zip": "12345"
                    },
                    "items": [
                        {
                            "name": "Test Product",
                            "price": 99.99,
                            "quantity": 1
                        }
                    ]
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                self.transaction_id = data.get("transaction_id")
                self.log_success(f"Payment processed: {self.transaction_id}")
                self.log_info(f"Signature: {data.get('signature', '')[:50]}...")
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
                self.log_success(f"Retrieved {len(data.get('transactions', []))} transactions")
                return True
            else:
                self.log_error(f"Failed to list transactions: {response.text}")
                return False
        except Exception as e:
            self.log_error(f"List transactions error: {e}")
            return False
    
    def test_verify_transaction(self):
        """Test 6: Verify Transaction"""
        if not self.transaction_id:
            self.log_info("Skipping verification - no transaction ID")
            return True
            
        self.log_info(f"Verifying transaction: {self.transaction_id}")
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.post(
                f"{self.api_url}/api/payments/verify",
                headers=headers,
                json={"transaction_id": self.transaction_id}
            )
            
            if response.status_code == 200:
                data = response.json()
                is_valid = data.get("is_valid", False)
                self.log_success(f"Transaction verification: {'Valid' if is_valid else 'Invalid'}")
                return True
            else:
                self.log_error(f"Verification failed: {response.text}")
                return False
        except Exception as e:
            self.log_error(f"Verification error: {e}")
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
            if response.status_code == 200 and "payment_amount_usd" in response.text:
                self.log_success("Metrics endpoint working")
                return True
            else:
                self.log_error("Metrics endpoint failed")
                return False
        except Exception as e:
            self.log_error(f"Metrics error: {e}")
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
        print(f"\n{Fore.CYAN}{'='*50}")
        print(f"{Fore.CYAN}Quantum-Secure E-Commerce API Test Suite")
        print(f"{Fore.CYAN}{'='*50}\n")
        
        tests = [
            self.test_health_check,
            self.test_register,
            self.test_login,
            self.test_payment,
            self.test_transactions_list,
            self.test_verify_transaction,
            self.test_crypto_endpoints,
            self.test_metrics,
            self.test_admin_protection
        ]
        
        for i, test in enumerate(tests, 1):
            print(f"\n{Fore.BLUE}Test {i}: {test.__doc__}")
            test()
            time.sleep(0.5)  # Small delay between tests
        
        # Summary
        print(f"\n{Fore.CYAN}{'='*50}")
        print(f"{Fore.CYAN}Test Summary")
        print(f"{Fore.CYAN}{'='*50}\n")
        
        passed = sum(1 for result, _ in self.test_results if result == "PASS")
        failed = sum(1 for result, _ in self.test_results if result == "FAIL")
        
        print(f"{Fore.GREEN}Passed: {passed}")
        print(f"{Fore.RED}Failed: {failed}")
        print(f"{Fore.YELLOW}Total: {passed + failed}")
        
        if failed == 0:
            print(f"\n{Fore.GREEN}{'🎉 All tests passed! API is working correctly.'}")
        else:
            print(f"\n{Fore.RED}{'⚠️  Some tests failed. Please check the errors above.'}")
            
        return failed == 0


if __name__ == "__main__":
    tester = APITester()
    success = tester.run_all_tests()
    exit(0 if success else 1)