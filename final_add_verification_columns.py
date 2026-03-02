#!/usr/bin/env python3
"""
Simple database column fixer
Uses the same connection pattern as the app to ensure consistency
"""

import mysql.connector
import os
from dotenv import load_dotenv
import sys
import time

# Load environment
load_dotenv(os.path.join(os.path.dirname(__file__), 'backend', '.env'))

def check_column_exists(cursor, table, column):
    """Check if a column exists in a table"""
    try:
        cursor.execute(f"SHOW COLUMNS FROM `{table}` WHERE Field='{column}'")
        result = cursor.fetchall()  # Make sure to fetch all results
        return len(result) > 0
    except mysql.connector.Error as e:
        return False

def main():
    # Delay to ensure any locks are released
    print("Waiting for database to be ready...")
    time.sleep(3)
    
    try:
        # Create fresh connection
        db = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", "root"),
            database=os.getenv("DB_NAME", "civictrack_ai"),
            autocommit=True,
            connection_timeout=10
        )
        
        cursor = db.cursor()
        print("✓ Connected to database\n")
        
        # List of columns to add
        columns_to_add = [
            ("issues", "verification_status", "VARCHAR(50) DEFAULT 'Pending'"),
            ("issues", "verified_by", "INT DEFAULT NULL"),
            ("issue_resolutions", "image_path", "VARCHAR(255)"),
        ]
        
        # Try to add each column
        for table, column, type_def in columns_to_add:
            if check_column_exists(cursor, table, column):
                print(f"✓ {table}.{column} already exists")
            else:
                print(f"Adding {table}.{column}...")
                try:
                    cursor.execute(f"ALTER TABLE `{table}` ADD COLUMN `{column}` {type_def}")
                    print(f"  ✓ Column added successfully")
                except Exception as e:
                    print(f"  ✗ Error: {e}")
                    # Don't exit on error, continue with other columns
        
        # Try to add foreign key (won't fail if it already exists)
        try:
            cursor.execute("""
                ALTER TABLE `issues` 
                ADD CONSTRAINT fk_verified_by 
                FOREIGN KEY (`verified_by`) REFERENCES `users`(`id`) ON DELETE SET NULL
            """)
            print("✓ Foreign key fk_verified_by added")
        except mysql.connector.Error as e:
            if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                print("✓ Foreign key fk_verified_by already exists")
            else:
                print(f"Note: {e}")
        
        # Add indexes
        for col in ["verification_status", "verified_by"]:
            try:        
                cursor.execute(f"ALTER TABLE `issues` ADD INDEX `idx_{col}` (`{col}`)")
                print(f"✓ Index idx_{col} added")
            except mysql.connector.Error as e:
                if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                    print(f"✓ Index idx_{col} already exists")
                else:
                    print(f"Note: {e}")
        
        cursor.close()
        db.close()
        
        print("\n✓ Database migration complete!")
        return 0
        
    except Exception as e:
        print(f"✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
