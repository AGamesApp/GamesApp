#!/usr/bin/env python3
"""
Test script to verify Google OAuth fixes
"""
import requests
import json

def test_google_auth_endpoint():
    """Test the Google OAuth endpoint with various scenarios"""
    
    url = "https://games.agames.cv/api/users/auth/google/"
    
    print("=== Testing Google OAuth Endpoint ===")
    
    # Test 1: Missing id_token
    print("\n1. Testing missing id_token...")
    response = requests.post(url, json={})
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    # Test 2: Invalid id_token
    print("\n2. Testing invalid id_token...")
    response = requests.post(url, json={"id_token": "invalid_token_123"})
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    # Test 3: Check endpoint accessibility
    print("\n3. Testing endpoint accessibility...")
    try:
        response = requests.get(url, timeout=5)
        print(f"GET Status: {response.status_code}")
    except Exception as e:
        print(f"GET Error: {str(e)}")

if __name__ == "__main__":
    test_google_auth_endpoint()