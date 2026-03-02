#!/usr/bin/env python3
"""
CivicTrack AI - Complete Startup Script
Starts backend and frontend servers
"""

import subprocess
import time
import os
import sys
from pathlib import Path

def print_header():
    print("\n" + "="*70)
    print("  CivicTrack AI - System Startup")
    print("="*70 + "\n")

def print_section(title):
    print(f"\n{title}")
    print("-" * len(title))

def start_backend():
    print_section("1. Starting Backend Server")
    backend_path = Path(__file__).parent / "backend" / "app.py"
    
    if not backend_path.exists():
        print("✗ Backend app.py not found!")
        return None
    
    print("Starting Python Flask server on localhost:5000...")
    process = subprocess.Popen(
        [sys.executable, str(backend_path)],
        cwd=backend_path.parent,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    # Wait for backend to start
    time.sleep(3)
    print("✓ Backend started (PID: {})".format(process.pid))
    return process

def start_frontend():
    print_section("2. Starting Frontend Server")
    frontend_path = Path(__file__).parent / "frontend"
    
    if not frontend_path.exists():
        print("✗ Frontend directory not found!")
        return None
    
    print("Starting HTTP server on localhost:8000...")
    process = subprocess.Popen(
        [sys.executable, "-m", "http.server", "8000"],
        cwd=frontend_path,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    time.sleep(2)
    print("✓ Frontend started (PID: {})".format(process.pid))
    return process

def print_instructions():
    print_section("3. System Ready!")
    print("\n✓ Backend: http://127.0.0.1:5000")
    print("✓ Frontend: http://localhost:8000\n")
    
    print("Login Credentials:")
    print("-" * 40)
    print("\nAdmin User:")
    print("  Email: admin@gmail.com")
    print("  Password: admin123")
    print("  Dashboard: http://localhost:8000/dashboard.html")
    
    print("\nResolver User:")
    print("  Email: resolver@example.com")
    print("  Password: resolver123")
    print("  Dashboard: http://localhost:8000/resolver.html")
    
    print("\nCitizen User:")
    print("  Email: user@gmail.com")
    print("  Dashboard: http://localhost:8000/citizen.html")
    
    print("\nSystem Tester:")
    print("  URL: http://localhost:8000/tester.html")
    
    print("\n" + "="*70)
    print("Press CTRL+C to stop servers")
    print("="*70 + "\n")

def main():
    print_header()
    
    # Check if running from correct directory
    if not Path("backend/app.py").exists():
        print("✗ Error: Run this script from the CivicTrack AI root directory!")
        sys.exit(1)
    
    backend_process = start_backend()
    frontend_process = start_frontend()
    
    if backend_process and frontend_process:
        print_instructions()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print_section("Shutting Down")
            print("Stopping servers...")
            
            if backend_process:
                backend_process.terminate()
                print("✓ Backend stopped")
            
            if frontend_process:
                frontend_process.terminate()
                print("✓ Frontend stopped")
            
            print("\nGoodbye!\n")
    else:
        print("✗ Failed to start servers")
        sys.exit(1)

if __name__ == "__main__":
    main()
