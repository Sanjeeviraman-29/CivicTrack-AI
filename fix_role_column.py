#!/usr/bin/env python3
"""
Fix users table role column to include 'resolver'
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
    
    print("Updating role column to include 'resolver'...")
    cursor.execute("""
        ALTER TABLE users MODIFY COLUMN role ENUM('citizen', 'admin', 'resolver') DEFAULT 'citizen'
    """)
    db.commit()
    print("✓ Role column updated\n")
    
    cursor.close()
    db.close()
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
