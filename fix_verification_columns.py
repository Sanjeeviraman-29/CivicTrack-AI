#!/usr/bin/env python3
"""
Quick fix to add verification columns to database
"""

import mysql.connector
from dotenv import load_dotenv
import os
import sys

load_dotenv(os.path.join(os.path.dirname(__file__), 'backend', '.env'))

try:
    db = mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", "root"),
        database=os.getenv("DB_NAME", "civictrack_ai")
    )
    cursor = db.cursor()
    print("✓ Connected to database\n")
    
    # Check if verification_status already exists
    cursor.execute("SHOW COLUMNS FROM issues WHERE Field='verification_status'")
    if cursor.fetchone():
        print("✓ verification_status column already exists")
    else:
        print("Adding verification_status column...")
        try:
            cursor.execute("""
                ALTER TABLE issues 
                ADD COLUMN verification_status VARCHAR(50) DEFAULT 'Pending'
            """)
            db.commit()
            print("✓ verification_status column added")
        except Exception as e:
            print(f"Error adding verification_status: {e}")
    
    # Check if verified_by already exists
    cursor.execute("SHOW COLUMNS FROM issues WHERE Field='verified_by'")
    if cursor.fetchone():
        print("✓ verified_by column already exists")
    else:
        print("Adding verified_by column...")
        try:
            cursor.execute("""
                ALTER TABLE issues 
                ADD COLUMN verified_by INT DEFAULT NULL
            """)
            db.commit()
            print("✓ verified_by column added")
        except Exception as e:
            print(f"Error adding verified_by: {e}")
    
    # Check if foreign key for verified_by exists
    cursor.execute("SELECT CONSTRAINT_NAME FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE WHERE TABLE_NAME='issues' AND COLUMN_NAME='verified_by' AND REFERENCED_TABLE_NAME='users'")
    if not cursor.fetchone():
        print("Adding foreign key for verified_by...")
        try:
            cursor.execute("""
                ALTER TABLE issues 
                ADD CONSTRAINT fk_verified_by 
                FOREIGN KEY (verified_by) REFERENCES users(id) ON DELETE SET NULL
            """)
            db.commit()
            print("✓ Foreign key added for verified_by")
        except Exception as e:
            if "already exists" in str(e).lower():
                print("✓ Foreign key for verified_by already exists")
            else:
                print(f"Note: {e}")
    else:
        print("✓ Foreign key for verified_by already exists")
    
    # Check if image_path column exists in issue_resolutions
    cursor.execute("SHOW COLUMNS FROM issue_resolutions WHERE Field='image_path'")
    if cursor.fetchone():
        print("✓ image_path column already exists in issue_resolutions")
    else:
        print("Adding image_path column to issue_resolutions...")
        try:
            cursor.execute("""
                ALTER TABLE issue_resolutions 
                ADD COLUMN image_path VARCHAR(255) AFTER comments
            """)
            db.commit()
            print("✓ image_path column added to issue_resolutions")
        except Exception as e:
            print(f"Error adding image_path: {e}")
    
    # Add indexes
    print("\nAdding indexes...")
    
    for col in ['verification_status', 'verified_by']:
        cursor.execute(f"SHOW INDEX FROM issues WHERE Column_name='{col}'")
        if not cursor.fetchone():
            try:
                cursor.execute(f"ALTER TABLE issues ADD INDEX idx_{col} ({col})")
                db.commit()
                print(f"✓ Index on {col} added")
            except Exception as e:
                if "already exists" in str(e).lower():
                    print(f"✓ Index on {col} already exists")
                else:
                    print(f"Note: {e}")
        else:
            print(f"✓ Index on {col} already exists")
    
    print("\n✓ Database migration complete!")
    cursor.close()
    db.close()
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
