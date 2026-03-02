#!/usr/bin/env python3
"""
Verify database schema has all required columns
"""

import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), 'backend', '.env'))

db = mysql.connector.connect(
    host=os.getenv("DB_HOST", "localhost"),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD", "root"),
    database=os.getenv("DB_NAME", "civictrack_ai")
)

cursor = db.cursor()

# Check issues table columns
print("Issues table columns related to verification:")
cursor.execute("SHOW COLUMNS FROM issues")
columns = cursor.fetchall()

required_columns = ['verification_status', 'verified_by']
found_columns = [col[0] for col in columns]

for col in required_columns:
    if col in found_columns:
        print(f"  ✓ {col}")
    else:
        print(f"  ✗ {col} MISSING")

# Check issue_resolutions table
print("\nIssue resolutions table:")
cursor.execute("SHOW COLUMNS FROM issue_resolutions")
columns = cursor.fetchall()
found_columns = [col[0] for col in columns]

if 'image_path' in found_columns:
    print(f"  ✓ image_path")
else:
    print(f"  ✗ image_path MISSING")

cursor.close()
db.close()

print("\n✓ Schema verification complete!")
