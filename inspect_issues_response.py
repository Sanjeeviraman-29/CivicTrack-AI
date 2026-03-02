#!/usr/bin/env python3
"""
Test what /all-issues returns
"""

import requests
import json
import sys

BASE_URL = "http://127.0.0.1:5000"

# Login as admin
print("Getting admin token...\n")
login_response = requests.post(f"{BASE_URL}/login", json={
    "email": "admin@gmail.com",
    "password": "admin123"
})

if login_response.status_code == 200:
    token = login_response.json().get("token")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test /all-issues endpoint
    print("Testing GET /all-issues...")
    issues_response = requests.get(f"{BASE_URL}/all-issues", headers=headers)
    
    if issues_response.status_code == 200:
        issues = issues_response.json()
        print(f"\nTotal issues: {len(issues)}\n")
        
        if issues:
            print("First issue structure:")
            first_issue = issues[0]
            print(f"Type: {type(first_issue)}")
            print(f"Length: {len(first_issue)}")
            print("\nColumns order:")
            # Try to figure out the columns
            # The order from SELECT * should be: id, title, description, category, severity, latitude, longitude, created_by, status, created_at, updated_at, assigned_to, resolved_at
            column_names = [
                "id", "title", "description", "category", "severity", 
                "latitude", "longitude", "created_by", "status", "created_at", 
                "updated_at", "assigned_to", "resolved_at"
            ]
            
            for i, value in enumerate(first_issue):
                col_name = column_names[i] if i < len(column_names) else f"unknown_{i}"
                print(f"  [{i}] {col_name}: {value}")
