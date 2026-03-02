#!/usr/bin/env python3
"""
Final System Verification
Tests all components to ensure everything is working
"""

import requests
import json
import sys

def print_header():
    print("\n" + "="*70)
    print("  CivicTrack AI - System Verification")
    print("="*70 + "\n")

def test_backend_health():
    print("1. Testing Backend Health...")
    try:
        response = requests.get("http://127.0.0.1:5000/health")
        if response.status_code == 200:
            print("   ✓ Backend is healthy")
            return True
        else:
            print("   ✗ Backend health check failed")
            return False
    except Exception as e:
        print(f"   ✗ Cannot reach backend: {e}")
        return False

def test_admin_login():
    print("\n2. Testing Admin Login...")
    try:
        response = requests.post("http://127.0.0.1:5000/login", json={
            "email": "admin@gmail.com",
            "password": "admin123"
        })
        
        if response.status_code == 200:
            token = response.json().get("token")
            print("   ✓ Admin login successful")
            return token
        else:
            print(f"   ✗ Login failed: {response.json()}")
            return None
    except Exception as e:
        print(f"   ✗ Login error: {e}")
        return None

def test_resolvers(token):
    print("\n3. Testing Get Resolvers...")
    try:
        response = requests.get("http://127.0.0.1:5000/resolvers", 
            headers={"Authorization": f"Bearer {token}"})
        
        if response.status_code == 200:
            resolvers = response.json()
            print(f"   ✓ Found {len(resolvers)} resolver(s)")
            for resolver in resolvers:
                print(f"     - {resolver['name']}")
            return len(resolvers) > 0
        else:
            print(f"   ✗ Failed to get resolvers: {response.json()}")
            return False
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False

def test_all_issues(token):
    print("\n4. Testing Get All Issues...")
    try:
        response = requests.get("http://127.0.0.1:5000/all-issues",
            headers={"Authorization": f"Bearer {token}"})
        
        if response.status_code == 200:
            issues = response.json()
            unassigned = sum(1 for issue in issues if not issue[11] or issue[11] is None)
            assigned = len(issues) - unassigned
            
            print(f"   ✓ Found {len(issues)} total issues")
            print(f"     - Unassigned: {unassigned}")
            print(f"     - Assigned: {assigned}")
            
            if unassigned > 0:
                issue = issues[0]
                print(f"     - Example: '{issue[1]}' (Status: {issue[8]})")
            
            return len(issues) > 0
        else:
            print(f"   ✗ Failed to get issues: {response.json()}")
            return False
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False

def test_status_stats(token):
    print("\n5. Testing Status Statistics...")
    try:
        response = requests.get("http://127.0.0.1:5000/status-stats",
            headers={"Authorization": f"Bearer {token}"})
        
        if response.status_code == 200:
            stats = response.json()
            print("   ✓ Status statistics:")
            total = 0
            for stat in stats:
                print(f"     - {stat['status']}: {stat['count']}")
                total += stat['count']
            print(f"     - Total: {total}")
            return True
        else:
            print(f"   ✗ Failed to get stats: {response.json()}")
            return False
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False

def test_assignment_flow(token):
    print("\n6. Testing Assignment Flow...")
    try:
        # Get first unassigned issue
        issues_resp = requests.get("http://127.0.0.1:5000/all-issues",
            headers={"Authorization": f"Bearer {token}"})
        issues = issues_resp.json()
        
        unassigned = [i for i in issues if not i[11] or i[11] is None]
        if not unassigned:
            print("   ⚠ No unassigned issues to test")
            return True
        
        issue_id = unassigned[0][0]
        
        # Get resolvers
        resolvers_resp = requests.get("http://127.0.0.1:5000/resolvers",
            headers={"Authorization": f"Bearer {token}"})
        resolvers = resolvers_resp.json()
        
        if not resolvers:
            print("   ⚠ No resolvers available")
            return True
        
        resolver_id = resolvers[0]['id']
        
        # Try to assign
        assign_resp = requests.post("http://127.0.0.1:5000/assign-issue",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json={"issue_id": issue_id, "resolver_id": resolver_id})
        
        if assign_resp.status_code == 200:
            print(f"   ✓ Successfully assigned issue {issue_id} to resolver")
            return True
        else:
            print(f"   ✗ Assignment failed: {assign_resp.json()}")
            return False
            
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False

def main():
    print_header()
    
    all_passed = True
    
    # Test 1: Backend health
    if not test_backend_health():
        print("\n" + "!"*70)
        print("BACKEND NOT RUNNING!")
        print("Start backend with: cd backend && python app.py")
        print("!"*70)
        return False
    
    # Test 2: Login
    token = test_admin_login()
    if not token:
        print("\n" + "!"*70)
        print("LOGIN FAILED!")
        print("Check admin credentials or database")
        print("!"*70)
        return False
    
    # Test 3-6: API endpoints
    all_passed = all([
        test_resolvers(token),
        test_all_issues(token),
        test_status_stats(token),
        test_assignment_flow(token)
    ]) and all_passed
    
    # Summary
    print("\n" + "="*70)
    if all_passed:
        print("✓ ALL TESTS PASSED!")
        print("\nYour CivicTrack AI system is fully functional!")
        print("\nNext steps:")
        print("1. Open http://localhost:8000 in browser")
        print("2. Login with: admin@gmail.com / admin123")
        print("3. Test work assignment on dashboard.html")
        print("4. Check http://localhost:8000/tester.html for more tests")
    else:
        print("✗ Some tests failed. Check errors above.")
    print("="*70 + "\n")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
