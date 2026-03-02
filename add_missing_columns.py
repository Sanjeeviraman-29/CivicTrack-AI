#!/usr/bin/env python3
"""
Add missing columns to database
"""

import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), 'backend', '.env'))

db = mysql.connector.connect(
    host=os.getenv("DB_HOST", "localhost"),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD", "root"),
    database=os.getenv("DB_NAME", "civictrack_ai"),
    autocommit=True
)

cursor = db.cursor()

# Add verified_by column
print("Adding verified_by column...")
try:
    cursor.execute("ALTER TABLE issues ADD COLUMN verified_by INT DEFAULT NULL")
    print("✓ verified_by column added")
except mysql.connector.Error as e:
    if "Duplicate" in str(e) or "already" in str(e).lower():
        print("✓ verified_by already exists")
    else:
        print(f"✗ Error: {e}")

# Add image_path column to issue_resolutions
print("\nAdding image_path column to issue_resolutions...")
try:
    cursor.execute("ALTER TABLE issue_resolutions ADD COLUMN image_path VARCHAR(255) AFTER comments")
    print("✓ image_path column added")
except mysql.connector.Error as e:
    if "Duplicate" in str(e) or "already" in str(e).lower():
        print("✓ image_path already exists")
    else:
        print(f"✗ Error: {e}")

# Add foreign key for verified_by
print("\nAdding foreign key for verified_by...")
try:
    cursor.execute("""
        ALTER TABLE issues 
        ADD CONSTRAINT fk_verified_by 
        FOREIGN KEY (verified_by) REFERENCES users(id) ON DELETE SET NULL
    """)
    print("✓ Foreign key added")
except mysql.connector.Error as e:
    if "Duplicate" in str(e) or "already" in str(e).lower():
        print("✓ Foreign key already exists")
    else:
        print(f"✗ Error: {e}")

# Add indexes
for col in ['verification_status', 'verified_by']:
    try:
        cursor.execute(f"ALTER TABLE issues ADD INDEX idx_{col} ({col})")
        print(f"✓ Index on {col} added")
    except mysql.connector.Error as e:
        if "Duplicate" in str(e) or "already" in str(e).lower():
            print(f"✓ Index on {col} already exists")
        else:
            print(f"✗ Error on {col}: {e}")

cursor.close()
db.close()

print("\n✓ Database migration complete!")
