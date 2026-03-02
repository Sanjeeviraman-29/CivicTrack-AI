#!/usr/bin/env python3
"""
Create a test issue for testing work assignment
"""

import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv(os.path.join(os.path.dirname(__file__), 'backend', '.env'))

try:
    db = mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME", "civictrack_ai")
    )
    cursor = db.cursor()
    print("✓ Connected to database\n")
    
    # Get a citizen user ID
    cursor.execute("SELECT id FROM users WHERE role='citizen' LIMIT 1")
    citizen = cursor.fetchone()
    
    if citizen:
        citizen_id = citizen[0]
        print(f"Creating test issue as citizen ID {citizen_id}...\n")
        
        # Insert a test issue
        cursor.execute("""
            INSERT INTO issues (title, description, category, severity, latitude, longitude, created_by, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            "Pothole on Main Street",
            "Large pothole near the traffic light",
            "Road Maintenance",
            "High",
            13.0827,
            80.2707,
            citizen_id,
            "Pending"
        ))
        db.commit()
        
        # Get the issue ID
        issue_id = cursor.lastrowid
        print(f"✓ Test issue created:")
        print(f"  ID: {issue_id}")
        print(f"  Title: Pothole on Main Street")
        print(f"  Status: Pending")
        print(f"  Location: 13.0827, 80.2707 (Chennai)")
        print(f"\nYou can now test assigning this issue to the resolver!\n")
    else:
        print("✗ No citizen user found. Please create one first.\n")
    
    cursor.close()
    db.close()
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
