#!/usr/bin/env python3
"""
Test the new endpoints
"""

import requests
import json
import sys
import os
from dotenv import load_dotenv

# Try to get a valid token for admin user
load_dotenv(os.path.join(os.path.dirname(__file__), 'backend', '.env'))

BASE_URL = "http://127.0.0.1:5000"

# First, login as admin
print("Testing backend endpoints...\n")
print("1. Login as admin...")

login_response = requests.post(f"{BASE_URL}/login", json={
    "email": "admin@gmail.com",
    "password": "admin123"  # Default password if it was changed
})

if login_response.status_code != 200:
    # Try with different password
    print("  First password didn't work, trying with setup password...")
    login_response = requests.post(f"{BASE_URL}/login", json={
        "email": "admin@gmail.com",
        "password": "password123"
    })

if login_response.status_code == 200:
    token = login_response.json().get("token")
    print(f"  ✓ Login successful, token: {token[:20]}...\n")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test /resolvers endpoint
    print("2. Testing GET /resolvers...")
    resolvers_response = requests.get(f"{BASE_URL}/resolvers", headers=headers)
    print(f"  Status: {resolvers_response.status_code}")
    print(f"  Response: {json.dumps(resolvers_response.json(), indent=2)}\n")
    
    # Test /all-issues endpoint
    print("3. Testing GET /all-issues...")
    issues_response = requests.get(f"{BASE_URL}/all-issues", headers=headers)
    print(f"  Status: {issues_response.status_code}")
    if issues_response.status_code == 200:
        issues = issues_response.json()
        print(f"  Total issues: {len(issues)}")
        if issues:
            first_issue = issues[0]
            print(f"  First issue: {first_issue[1] if len(first_issue) > 1 else 'N/A'}\n")
    else:
        print(f"  Response: {issues_response.text}\n")
    
    # Test /status-stats endpoint
    print("4. Testing GET /status-stats...")
    stats_response = requests.get(f"{BASE_URL}/status-stats", headers=headers)
    print(f"  Status: {stats_response.status_code}")
    print(f"  Response: {json.dumps(stats_response.json(), indent=2)}\n")
    
else:
    print(f"  ✗ Login failed: {login_response.text}\n")
    sys.exit(1)

print("✓ All tests completed!")
