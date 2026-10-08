#!/usr/bin/env python3
"""
Comprehensive endpoint testing script for agames.fun API
Tests all endpoints for proper responses and functionality
"""
import requests
import json
from datetime import datetime

BASE_URL = "https://games.agames.cv"
API_URL = f"{BASE_URL}/api"

# Test credentials (you'll need to update these with real test user)
TEST_USER = {
    "email": "test@example.com",
    "password": "testpass123"
}

class EndpointTester:
    def __init__(self):
        self.results = []
        self.token = None
        
    def test(self, name, method, endpoint, expected_status=200, data=None, headers=None, auth=False):
        """Test a single endpoint"""
        url = f"{API_URL}{endpoint}"
        
        test_headers = headers or {}
        if auth and self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=10, verify=True)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=10, verify=True)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=10, verify=True)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=10, verify=True)
            else:
                response = None
            
            status = response.status_code
            success = status == expected_status
            
            # Try to parse JSON response
            try:
                response_data = response.json()
                data_preview = str(response_data)[:200] if response_data else "No data"
            except:
                data_preview = response.text[:200] if response.text else "No content"
            
            result = {
                'name': name,
                'method': method,
                'endpoint': endpoint,
                'expected': expected_status,
                'actual': status,
                'success': success,
                'time': response.elapsed.total_seconds(),
                'data_preview': data_preview
            }
            
            self.results.append(result)
            
            status_icon = "✓" if success else "✗"
            status_color = "\033[92m" if success else "\033[91m"
            reset_color = "\033[0m"
            
            print(f"{status_color}{status_icon}{reset_color} {method:6} {endpoint:50} {status:3} ({response.elapsed.total_seconds()*1000:.0f}ms)")
            
            if not success:
                print(f"  Expected {expected_status}, got {status}")
                print(f"  Response: {data_preview}")
            
            return response
            
        except Exception as e:
            result = {
                'name': name,
                'method': method,
                'endpoint': endpoint,
                'expected': expected_status,
                'actual': 'ERROR',
                'success': False,
                'time': 0,
                'data_preview': str(e)
            }
            self.results.append(result)
            print(f"✗ {method:6} {endpoint:50} ERROR - {str(e)}")
            return None
    
    def print_summary(self):
        """Print test summary"""
        total = len(self.results)
        passed = sum(1 for r in self.results if r['success'])
        failed = total - passed
        
        print(f"\n{'='*80}")
        print(f"TEST SUMMARY")
        print(f"{'='*80}")
        print(f"Total Tests: {total}")
        print(f"Passed: {passed} ({passed/total*100:.1f}%)")
        print(f"Failed: {failed} ({failed/total*100:.1f}%)")
        
        if failed > 0:
            print(f"\nFailed Tests:")
            for result in self.results:
                if not result['success']:
                    print(f"  ✗ {result['method']} {result['endpoint']} - Expected {result['expected']}, got {result['actual']}")
        
        print(f"{'='*80}\n")

def main():
    print(f"\n{'='*80}")
    print(f"COMPREHENSIVE API ENDPOINT TEST")
    print(f"Base URL: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}\n")
    
    tester = EndpointTester()
    
    # ====================================
    # PUBLIC ENDPOINTS (No Auth Required)
    # ====================================
    print("\n" + "="*80)
    print("PUBLIC ENDPOINTS (No Authentication)")
    print("="*80 + "\n")
    
    # Emulators
    print("\n--- EMULATORS ---")
    tester.test("List Emulators", "GET", "/emulators/")
    
    # Get first emulator ID for testing
    emulator_response = requests.get(f"{API_URL}/emulators/", timeout=5)
    emulator_id = None
    if emulator_response.status_code == 200:
        try:
            emulators_data = emulator_response.json()
            # Handle both paginated and non-paginated responses
            if isinstance(emulators_data, dict) and 'results' in emulators_data:
                emulators = emulators_data['results']
            elif isinstance(emulators_data, list):
                emulators = emulators_data
            else:
                emulators = []
            
            if emulators and len(emulators) > 0:
                emulator_id = emulators[0]['id']
                tester.test("Get Emulator Detail", "GET", f"/emulators/{emulator_id}/")
        except Exception as e:
            print(f"  Warning: Could not parse emulators response: {e}")
    
    # Games
    print("\n--- GAMES ---")
    tester.test("List All Games", "GET", "/games/")
    
    if emulator_id:
        tester.test("List Games by Emulator", "GET", f"/games/?emulator={emulator_id}")
    
    tester.test("Search Games", "GET", "/games/?search=mario")
    tester.test("Filter Premium Games", "GET", "/games/?is_premium=true")
    tester.test("Games Pagination", "GET", "/games/?page=1&page_size=10")
    
    # Get first game ID for testing
    games_response = requests.get(f"{API_URL}/games/", timeout=5)
    game_id = None
    if games_response.status_code == 200:
        games = games_response.json()
        if 'results' in games and len(games['results']) > 0:
            game_id = games['results'][0]['id']
            tester.test("Get Game Detail", "GET", f"/games/{game_id}/")
            tester.test("Get Game Ratings", "GET", f"/games/{game_id}/ratings/")
            tester.test("Get Game Reviews", "GET", f"/games/{game_id}/reviews/")
    
    # Health Check
    print("\n--- SYSTEM ---")
    tester.test("Health Check", "GET", "/health/")
    
    # ====================================
    # AUTHENTICATION ENDPOINTS
    # ====================================
    print("\n" + "="*80)
    print("AUTHENTICATION ENDPOINTS")
    print("="*80 + "\n")
    
    # Note: These will fail if test credentials don't exist
    print("\n--- AUTH (Will fail without valid test credentials) ---")
    login_response = tester.test("Login", "POST", "/users/login/", 
                                 data=TEST_USER, expected_status=200)
    
    if login_response and login_response.status_code == 200:
        try:
            login_data = login_response.json()
            tester.token = login_data.get('access')
            print(f"  → Authenticated! Token obtained.")
        except:
            pass
    
    # Test token refresh (if we have a token)
    tester.test("Google OAuth Config", "GET", "/users/google-oauth-config/")
    
    # ====================================
    # AUTHENTICATED ENDPOINTS
    # ====================================
    if tester.token:
        print("\n" + "="*80)
        print("AUTHENTICATED ENDPOINTS")
        print("="*80 + "\n")
        
        print("\n--- USER PROFILE ---")
        tester.test("Get Current User Profile", "GET", "/users/me/", auth=True)
        tester.test("Update Profile", "PUT", "/users/me/", 
                   data={"username": "TestUser"}, auth=True)
        
        if game_id:
            print("\n--- GAME INTERACTIONS ---")
            tester.test("Rate Game", "POST", f"/games/{game_id}/rate/",
                       data={"score": 4.5}, auth=True)
            tester.test("Add Review", "POST", f"/games/{game_id}/review/",
                       data={"review": "Great game!", "score": 5.0}, auth=True)
            tester.test("Love Game", "POST", f"/games/{game_id}/love/", auth=True)
            tester.test("Download Game", "POST", f"/games/{game_id}/download/", auth=True)
            
            tester.test("My Loved Games", "GET", "/games/loved_games/", auth=True)
            tester.test("My Ratings", "GET", "/games/my_ratings/", auth=True)
        
        print("\n--- NOTIFICATIONS ---")
        tester.test("List Notifications", "GET", "/notifications/", auth=True)
        tester.test("Unread Notifications", "GET", "/notifications/unread/", auth=True)
    else:
        print("\n⚠ Skipping authenticated endpoints (no valid token)")
    
    # ====================================
    # INVALID ENDPOINTS (Expected to fail)
    # ====================================
    print("\n" + "="*80)
    print("INVALID ENDPOINTS (Expected to fail)")
    print("="*80 + "\n")
    
    tester.test("Invalid Endpoint", "GET", "/invalid/endpoint/", expected_status=404)
    tester.test("Invalid Game ID", "GET", "/games/999999/", expected_status=404)
    
    # ====================================
    # METHOD NOT ALLOWED TESTS
    # ====================================
    print("\n--- METHOD NOT ALLOWED TESTS ---")
    tester.test("POST to Emulators (Read-only)", "POST", "/emulators/", 
               expected_status=405, data={})
    
    # Print final summary
    tester.print_summary()
    
    # Performance analysis
    print("\nPERFORMANCE ANALYSIS")
    print("="*80)
    
    avg_time = sum(r['time'] for r in tester.results if isinstance(r['time'], (int, float))) / len(tester.results)
    max_time = max((r['time'] for r in tester.results if isinstance(r['time'], (int, float))), default=0)
    min_time = min((r['time'] for r in tester.results if isinstance(r['time'], (int, float))), default=0)
    
    print(f"Average Response Time: {avg_time*1000:.0f}ms")
    print(f"Fastest Response: {min_time*1000:.0f}ms")
    print(f"Slowest Response: {max_time*1000:.0f}ms")
    
    # Slowest endpoints
    slowest = sorted([r for r in tester.results if isinstance(r['time'], (int, float))], 
                     key=lambda x: x['time'], reverse=True)[:5]
    
    if slowest:
        print(f"\nSlowest Endpoints:")
        for r in slowest:
            print(f"  {r['method']:6} {r['endpoint']:50} {r['time']*1000:6.0f}ms")
    
    print(f"\n{'='*80}\n")

if __name__ == '__main__':
    main()
