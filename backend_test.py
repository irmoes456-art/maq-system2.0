#!/usr/bin/env python3
"""
Backend API Testing for Mastermaq Systems
Tests all specified endpoints with proper authentication
"""

import requests
import sys
import json
from datetime import datetime
import time

class MastermaqAPITester:
    def __init__(self, base_url="https://mastermaq-systems.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []
        self.session = requests.Session()
        self.session.timeout = 30

    def log(self, message):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'
        
        if headers:
            test_headers.update(headers)

        self.tests_run += 1
        self.log(f"🔍 Testing {name}...")
        self.log(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = self.session.get(url, headers=test_headers)
            elif method == 'POST':
                response = self.session.post(url, json=data, headers=test_headers)
            elif method == 'PUT':
                response = self.session.put(url, json=data, headers=test_headers)
            elif method == 'DELETE':
                response = self.session.delete(url, headers=test_headers)

            success = response.status_code == expected_status
            
            if success:
                self.tests_passed += 1
                self.log(f"✅ PASSED - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if isinstance(response_data, dict) and len(response_data) <= 3:
                        self.log(f"   Response: {response_data}")
                    elif isinstance(response_data, list) and len(response_data) <= 2:
                        self.log(f"   Response: {len(response_data)} items")
                    else:
                        self.log(f"   Response: {type(response_data).__name__} with data")
                except:
                    self.log(f"   Response: {response.text[:100]}...")
            else:
                self.log(f"❌ FAILED - Expected {expected_status}, got {response.status_code}")
                self.log(f"   Response: {response.text[:200]}")
                self.failed_tests.append({
                    'name': name,
                    'expected': expected_status,
                    'actual': response.status_code,
                    'response': response.text[:200]
                })

            return success, response.json() if success and response.text else {}

        except Exception as e:
            self.log(f"❌ FAILED - Error: {str(e)}")
            self.failed_tests.append({
                'name': name,
                'error': str(e)
            })
            return False, {}

    def test_health_check(self):
        """Test basic health endpoint"""
        url = f"{self.base_url}/health"
        self.tests_run += 1
        self.log(f"🔍 Testing Health Check...")
        self.log(f"   URL: {url}")
        
        try:
            response = self.session.get(url)
            success = response.status_code == 200
            
            if success:
                self.tests_passed += 1
                self.log(f"✅ PASSED - Status: {response.status_code}")
                self.log(f"   Response: Health endpoint accessible")
            else:
                self.log(f"❌ FAILED - Expected 200, got {response.status_code}")
                self.failed_tests.append({
                    'name': 'Health Check',
                    'expected': 200,
                    'actual': response.status_code,
                    'response': response.text[:200]
                })
            
            return success
        except Exception as e:
            self.log(f"❌ FAILED - Error: {str(e)}")
            self.failed_tests.append({
                'name': 'Health Check',
                'error': str(e)
            })
            return False

    def test_login(self, email, password):
        """Test login and get token"""
        success, response = self.run_test(
            "Login Authentication",
            "POST",
            "auth/login",
            200,
            data={"email": email, "password": password}
        )
        
        if success and 'token' in response:
            self.token = response['token']
            self.log(f"   Token obtained: {self.token[:20]}...")
            return True
        return False

    def test_token_verification(self):
        """Test token verification"""
        success, response = self.run_test(
            "Token Verification",
            "GET",
            "auth/verify",
            200
        )
        return success and response.get('valid') == True

    def test_service_orders_list(self):
        """Test service orders list with pagination"""
        success, response = self.run_test(
            "Service Orders List (Paginated)",
            "GET",
            "service-orders?page=1&limit=5",
            200
        )
        
        if success:
            orders = response.get('orders', [])
            total = response.get('total', 0)
            self.log(f"   Found {len(orders)} orders out of {total} total")
            
            # Verify structure
            if orders and len(orders) > 0:
                first_order = orders[0]
                required_fields = ['os_number', 'customer_name', 'status']
                missing_fields = [f for f in required_fields if f not in first_order]
                if missing_fields:
                    self.log(f"   ⚠️  Missing fields in order: {missing_fields}")
                else:
                    self.log(f"   ✅ Order structure looks good")
        
        return success

    def test_overdue_orders(self):
        """Test overdue orders endpoint"""
        success, response = self.run_test(
            "Overdue Orders",
            "GET",
            "service-orders/overdue-at",
            200
        )
        
        if success:
            count = response.get('count', 0)
            orders = response.get('orders', [])
            self.log(f"   Found {count} overdue orders")
        
        return success

    def test_routes_list(self):
        """Test routes list"""
        success, response = self.run_test(
            "Routes List",
            "GET",
            "routes/",
            200
        )
        
        if success:
            if isinstance(response, list):
                self.log(f"   Found {len(response)} routes")
            else:
                self.log(f"   Response type: {type(response)}")
        
        return success

    def test_whatsapp_config(self):
        """Test WhatsApp configuration"""
        success, response = self.run_test(
            "WhatsApp Configuration",
            "GET",
            "whatsapp/config",
            200
        )
        return success

    def test_manuais_list(self):
        """Test manuais list"""
        success, response = self.run_test(
            "Manuais List",
            "GET",
            "manuais",
            200
        )
        
        if success:
            if isinstance(response, list):
                self.log(f"   Found {len(response)} manuais")
            elif isinstance(response, dict) and 'manuais' in response:
                self.log(f"   Found {len(response['manuais'])} manuais")
        
        return success

    def test_priority_api(self):
        """Test priority API functionality as specified in review request"""
        # Test PUT /api/service-orders/71765005 with {priority: true}
        success, response = self.run_test(
            "Priority API - Set Priority True",
            "PUT",
            "service-orders/71765005",
            200,
            data={"priority": True}
        )
        
        if success:
            priority_value = response.get('priority')
            if priority_value == True:
                self.log(f"   ✅ Priority correctly set to: {priority_value}")
            else:
                self.log(f"   ⚠️  Priority value unexpected: {priority_value}")
                success = False
        
        return success

    def test_search_functionality(self):
        """Test search functionality for Felipe as mentioned in review request"""
        # Test search for 'Felipe' - should return ~87 results
        success, response = self.run_test(
            "Search Functionality - Felipe",
            "GET",
            "service-orders?search=Felipe&limit=100",
            200
        )
        
        if success:
            total = response.get('total', 0)
            orders = response.get('orders', [])
            self.log(f"   Found {total} total results for 'Felipe' search")
            self.log(f"   Returned {len(orders)} orders in this page")
            
            # Check if Felipe appears in customer names
            felipe_count = 0
            for order in orders:
                customer_name = order.get('customer_name', '').lower()
                if 'felipe' in customer_name:
                    felipe_count += 1
            
            self.log(f"   {felipe_count} orders have 'Felipe' in customer name")
            
            # Verify search is working (should have some results)
            if total > 0:
                self.log(f"   ✅ Search returned results")
            else:
                self.log(f"   ⚠️  No search results found")
                success = False
        
        return success

    def test_additional_endpoints(self):
        """Test additional important endpoints"""
        endpoints = [
            ("Service Order Statuses", "GET", "service-orders/statuses", 200),
            ("Service Order Brands", "GET", "service-orders/brands", 200),
            ("Status Colors", "GET", "status-colors", 200),
            ("Telecontrol Status", "GET", "telecontrol/status", 200),
            ("Notifications Unread Count", "GET", "notifications/unread-count", 200),
        ]
        
        results = []
        for name, method, endpoint, expected_status in endpoints:
            success, response = self.run_test(name, method, endpoint, expected_status)
            results.append(success)
        
        return all(results)

    def run_all_tests(self):
        """Run all backend tests"""
        self.log("🚀 Starting Mastermaq Systems Backend API Tests")
        self.log(f"   Base URL: {self.base_url}")
        
        # Test 1: Health check
        if not self.test_health_check():
            self.log("❌ Health check failed - stopping tests")
            return False
        
        # Test 2: Login
        if not self.test_login("mastermaqassistencia@gmail.com", "atr132641"):
            self.log("❌ Login failed - stopping tests")
            return False
        
        # Test 3: Token verification
        if not self.test_token_verification():
            self.log("❌ Token verification failed")
        
        # Test 4: Service orders with pagination
        if not self.test_service_orders_list():
            self.log("❌ Service orders list failed")
        
        # Test 5: Overdue orders
        if not self.test_overdue_orders():
            self.log("❌ Overdue orders test failed")
        
        # Test 6: Routes
        if not self.test_routes_list():
            self.log("❌ Routes list failed")
        
        # Test 7: WhatsApp config
        if not self.test_whatsapp_config():
            self.log("❌ WhatsApp config failed")
        
        # Test 8: Manuais
        if not self.test_manuais_list():
            self.log("❌ Manuais list failed")
        
        # Test 9: Priority API (specific test from review request)
        if not self.test_priority_api():
            self.log("❌ Priority API test failed")
        
        # Test 10: Search functionality (Felipe search from review request)
        if not self.test_search_functionality():
            self.log("❌ Search functionality test failed")
        
        # Test 11: Additional endpoints
        if not self.test_additional_endpoints():
            self.log("❌ Some additional endpoints failed")
        
        return True

    def print_summary(self):
        """Print test summary"""
        self.log("\n" + "="*60)
        self.log("📊 TEST SUMMARY")
        self.log("="*60)
        self.log(f"Total tests run: {self.tests_run}")
        self.log(f"Tests passed: {self.tests_passed}")
        self.log(f"Tests failed: {self.tests_run - self.tests_passed}")
        self.log(f"Success rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if self.failed_tests:
            self.log("\n❌ FAILED TESTS:")
            for i, test in enumerate(self.failed_tests, 1):
                self.log(f"{i}. {test['name']}")
                if 'error' in test:
                    self.log(f"   Error: {test['error']}")
                else:
                    self.log(f"   Expected: {test['expected']}, Got: {test['actual']}")
                    self.log(f"   Response: {test['response']}")
        
        return self.tests_passed == self.tests_run

def main():
    """Main test execution"""
    tester = MastermaqAPITester()
    
    try:
        tester.run_all_tests()
        success = tester.print_summary()
        return 0 if success else 1
    except KeyboardInterrupt:
        tester.log("\n⚠️  Tests interrupted by user")
        return 1
    except Exception as e:
        tester.log(f"\n💥 Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())