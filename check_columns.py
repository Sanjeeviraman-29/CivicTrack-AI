#!/usr/bin/env python3
"""
Check if verification columns exist in database
"""

import mysql.connector
import os
from dotenv import load_dotenv
import sys

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), 'backend', '.env'))

try:
    # Connect with timeout
    db = mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", "root"),
        database=os.getenv("DB_NAME", "civictrack_ai"),
        connection_timeout=5
    )
    
    cursor = db.cursor()
    cursor.execute("DESCRIBE issues")
    columns = cursor.fetchall()
    
    print("Current columns in issues table:")
    for col in columns:
        print(f"  - {col[0]}: {col[1]}")
    
    # Check specifically for verification columns
    column_names = [col[0] for col in columns]
    if 'verification_status' in column_names:
        print("\n✓ verification_status column EXISTS")
    else:
        print("\n✗ verification_status column MISSING")
    
    if 'verified_by' in column_names:
        print("✓ verified_by column EXISTS")
    else:
        print("✗ verified_by column MISSING")
    
    cursor.close()
    db.close()
    
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
