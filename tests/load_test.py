#!/usr/bin/env python3
"""
Load testing script to determine max concurrent users for the game server.
Tests various endpoints with increasing concurrent users.
"""
import requests
import time
import threading
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
import json

# Configuration
BASE_URL = "https://agames.fun"
API_BASE = f"{BASE_URL}/api"

# Test scenarios
SCENARIOS = {
    "list_emulators": f"{API_BASE}/emulators/",
    "list_games": f"{API_BASE}/games/?emulator=1",
    "game_detail": f"{API_BASE}/games/1/",
    "search_games": f"{API_BASE}/games/?search=mario",
}

class LoadTester:
    def __init__(self):
        self.results = defaultdict(list)
        self.errors = defaultdict(int)
        self.response_times = defaultdict(list)
        
    def make_request(self, endpoint_name, url, timeout=10):
        """Make a single request and record metrics."""
        start_time = time.time()
        try:
            response = requests.get(url, timeout=timeout, verify=True)
            elapsed = time.time() - start_time
            
            self.response_times[endpoint_name].append(elapsed)
            
            if response.status_code == 200:
                self.results[endpoint_name].append('success')
                return True, elapsed, response.status_code
            else:
                self.results[endpoint_name].append('error')
                self.errors[f"{endpoint_name}_status_{response.status_code}"] += 1
                return False, elapsed, response.status_code
                
        except requests.exceptions.Timeout:
            elapsed = time.time() - start_time
            self.results[endpoint_name].append('timeout')
            self.errors[f"{endpoint_name}_timeout"] += 1
            return False, elapsed, 'timeout'
            
        except Exception as e:
            elapsed = time.time() - start_time
            self.results[endpoint_name].append('error')
            self.errors[f"{endpoint_name}_error"] += 1
            return False, elapsed, str(e)
    
    def test_concurrent_users(self, num_users, requests_per_user=5):
        """Test with a specific number of concurrent users."""
        print(f"\n{'='*70}")
        print(f"Testing with {num_users} concurrent users ({requests_per_user} requests each)")
        print(f"{'='*70}")
        
        test_start = time.time()
        total_requests = num_users * requests_per_user
        
        with ThreadPoolExecutor(max_workers=num_users) as executor:
            futures = []
            
            # Submit all requests
            for user_id in range(num_users):
                for req_num in range(requests_per_user):
                    # Rotate through different endpoints
                    endpoint_name = list(SCENARIOS.keys())[req_num % len(SCENARIOS)]
                    url = SCENARIOS[endpoint_name]
                    future = executor.submit(self.make_request, endpoint_name, url)
                    futures.append((endpoint_name, future))
            
            # Wait for completion
            completed = 0
            for endpoint_name, future in futures:
                try:
                    future.result(timeout=30)
                    completed += 1
                    if completed % 10 == 0:
                        print(f"  Progress: {completed}/{total_requests} requests completed...", end='\r')
                except Exception as e:
                    self.errors[f"{endpoint_name}_exception"] += 1
        
        test_duration = time.time() - test_start
        
        # Calculate metrics
        total_success = sum(1 for endpoint_results in self.results.values() 
                          for r in endpoint_results if r == 'success')
        total_errors = sum(1 for endpoint_results in self.results.values() 
                         for r in endpoint_results if r != 'success')
        
        all_response_times = []
        for times in self.response_times.values():
            all_response_times.extend(times)
        
        print(f"\n\n  Test Duration: {test_duration:.2f} seconds")
        print(f"  Total Requests: {total_requests}")
        print(f"  Successful: {total_success} ({total_success/total_requests*100:.1f}%)")
        print(f"  Failed: {total_errors} ({total_errors/total_requests*100:.1f}%)")
        print(f"  Requests/second: {total_requests/test_duration:.2f}")
        
        if all_response_times:
            print(f"\n  Response Time Statistics:")
            print(f"    Min: {min(all_response_times)*1000:.0f}ms")
            print(f"    Max: {max(all_response_times)*1000:.0f}ms")
            print(f"    Mean: {statistics.mean(all_response_times)*1000:.0f}ms")
            print(f"    Median: {statistics.median(all_response_times)*1000:.0f}ms")
            if len(all_response_times) > 1:
                print(f"    Std Dev: {statistics.stdev(all_response_times)*1000:.0f}ms")
        
        # Per-endpoint stats
        print(f"\n  Per-Endpoint Performance:")
        for endpoint_name, times in self.response_times.items():
            if times:
                successes = sum(1 for r in self.results[endpoint_name] if r == 'success')
                total = len(self.results[endpoint_name])
                print(f"    {endpoint_name:20s}: {statistics.mean(times)*1000:6.0f}ms avg, "
                      f"{successes}/{total} success ({successes/total*100:.0f}%)")
        
        if self.errors:
            print(f"\n  Errors:")
            for error_type, count in sorted(self.errors.items(), key=lambda x: x[1], reverse=True):
                print(f"    {error_type}: {count}")
        
        # Determine if system handled the load well
        success_rate = total_success / total_requests if total_requests > 0 else 0
        avg_response_time = statistics.mean(all_response_times) if all_response_times else 0
        
        return {
            'users': num_users,
            'success_rate': success_rate,
            'avg_response_time': avg_response_time,
            'requests_per_second': total_requests/test_duration if test_duration > 0 else 0,
            'max_response_time': max(all_response_times) if all_response_times else 0,
        }


def main():
    print(f"\n{'#'*70}")
    print(f"# Load Testing: {BASE_URL}")
    print(f"# Server: Hetzner CPX22 (3 vCPU, 4GB RAM, 7 Gunicorn workers)")
    print(f"{'#'*70}")
    
    # First, test connectivity
    print(f"\nTesting connectivity...")
    try:
        response = requests.get(f"{API_BASE}/emulators/", timeout=5)
        print(f"✓ Server is reachable (Status: {response.status_code})")
    except Exception as e:
        print(f"✗ Server connection failed: {e}")
        return
    
    # Progressive load testing
    test_levels = [
        (10, 5),    # 10 users, 5 requests each = 50 total
        (25, 5),    # 25 users, 5 requests each = 125 total
        (50, 5),    # 50 users, 5 requests each = 250 total
        (75, 5),    # 75 users, 5 requests each = 375 total
        (100, 5),   # 100 users, 5 requests each = 500 total
        (150, 5),   # 150 users, 5 requests each = 750 total
        (200, 5),   # 200 users, 5 requests each = 1000 total
    ]
    
    results_summary = []
    
    for num_users, requests_per_user in test_levels:
        tester = LoadTester()
        result = tester.test_concurrent_users(num_users, requests_per_user)
        results_summary.append(result)
        
        # Stop if success rate drops below 90% or response time > 5 seconds
        if result['success_rate'] < 0.90:
            print(f"\n⚠ Success rate dropped below 90%. Server limit reached.")
            break
        if result['avg_response_time'] > 5.0:
            print(f"\n⚠ Average response time exceeded 5 seconds. Server limit reached.")
            break
        
        # Small pause between test levels
        time.sleep(2)
    
    # Final summary
    print(f"\n\n{'='*70}")
    print(f"LOAD TEST SUMMARY")
    print(f"{'='*70}")
    print(f"{'Users':<10} {'Success Rate':<15} {'Avg Response':<15} {'Req/sec':<12}")
    print(f"{'-'*70}")
    
    for result in results_summary:
        print(f"{result['users']:<10} {result['success_rate']*100:>6.1f}%        "
              f"{result['avg_response_time']*1000:>8.0f}ms        "
              f"{result['requests_per_second']:>8.1f}")
    
    # Recommendation
    print(f"\n{'='*70}")
    print(f"RECOMMENDATION")
    print(f"{'='*70}")
    
    # Find the highest level with >95% success and <2s response time
    good_results = [r for r in results_summary 
                   if r['success_rate'] > 0.95 and r['avg_response_time'] < 2.0]
    
    if good_results:
        max_users = max(r['users'] for r in good_results)
        print(f"\n✓ Server can comfortably handle: {max_users} concurrent users")
        print(f"  (with >95% success rate and <2s response time)")
    
    # Find absolute max
    acceptable_results = [r for r in results_summary if r['success_rate'] > 0.90]
    if acceptable_results:
        max_acceptable = max(r['users'] for r in acceptable_results)
        print(f"\n✓ Maximum capacity: {max_acceptable} concurrent users")
        print(f"  (with >90% success rate)")
    
    print(f"\n{'='*70}\n")


if __name__ == '__main__':
    main()
