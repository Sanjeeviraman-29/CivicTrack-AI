#!/usr/bin/env python3
"""
Add verification columns with autocommit to avoid locking
"""

import mysql.connector
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), 'backend', '.env'))

print("Attempting to add verification columns...")

# Use autocommit to execute each statement immediately
db = mysql.connector.connect(
    host=os.getenv("DB_HOST", "localhost"),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD", "root"),
    database=os.getenv("DB_NAME", "civictrack_ai"),
    autocommit=True,
    connection_timeout=5
)

cursor = db.cursor()

# List of SQL statements to execute
statements = [
    "ALTER TABLE issues ADD COLUMN verification_status VARCHAR(50) DEFAULT 'Pending'",
    "ALTER TABLE issues ADD COLUMN verified_by INT DEFAULT NULL",
    "ALTER TABLE issue_resolutions ADD COLUMN image_path VARCHAR(255)",
]

for statement in statements:
    try:
        print(f"Executing: {statement[:50]}...")
        cursor.execute(statement)
        print(f"  ✓ Success")
    except mysql.connector.Error as e:
        if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
            print(f"  ✓ Already exists (OK)")
        else:
            print(f"  ✗ Error: {e}")

cursor.close()
db.close()

print("\nDone!")
