#!/usr/bin/env python3
"""
Check issues table structure and fix any issues
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
    
    print("Issues table structure:")
    cursor.execute("DESCRIBE issues")
    columns = cursor.fetchall()
    for col in columns:
        print(f"  {col[0]}: {col[1]} (NULL: {col[2]})")
    
    # Fix status column if needed
    print("\nFixing status column...")
    cursor.execute("""
        ALTER TABLE issues MODIFY COLUMN status ENUM('Pending', 'Assigned', 'In Progress', 'Resolved') DEFAULT 'Pending'
    """)
    db.commit()
    print("✓ Status column updated to include 'Assigned' status")
    
    cursor.close()
    db.close()
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
