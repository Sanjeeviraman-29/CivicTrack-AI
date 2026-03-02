#!/usr/bin/env python3
"""
Database setup script to create necessary tables if they don't exist
"""

import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv(os.path.join(os.path.dirname(__file__), 'backend', '.env'))

try:
    db = mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", "root"),
        database=os.getenv("DB_NAME", "civictrack_ai")
    )
    cursor = db.cursor()
    print("✓ Connected to database")
    
    # Check and add columns to issues table
    print("\nAdding columns to issues table if they don't exist...")
    
    # Check if assigned_to column exists
    cursor.execute("SHOW COLUMNS FROM issues WHERE Field='assigned_to'")
    if not cursor.fetchone():
        print("  Adding assigned_to column...")
        cursor.execute("""
            ALTER TABLE issues 
            ADD COLUMN assigned_to INT DEFAULT NULL,
            ADD FOREIGN KEY (assigned_to) REFERENCES users(id) ON DELETE SET NULL
        """)
        db.commit()
        print("  ✓ assigned_to column added")
    else:
        print("  - assigned_to column already exists")
    
    # Check if resolved_at column exists
    cursor.execute("SHOW COLUMNS FROM issues WHERE Field='resolved_at'")
    if not cursor.fetchone():
        print("  Adding resolved_at column...")
        cursor.execute("""
            ALTER TABLE issues 
            ADD COLUMN resolved_at TIMESTAMP DEFAULT NULL
        """)
        db.commit()
        print("  ✓ resolved_at column added")
    else:
        print("  - resolved_at column already exists")
    
    # Create issue_assignments table if it doesn't exist
    print("\nCreating issue_assignments table if it doesn't exist...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS issue_assignments (
            id INT AUTO_INCREMENT PRIMARY KEY,
            issue_id INT NOT NULL,
            assigned_by INT NOT NULL,
            assigned_to INT NOT NULL,
            assignment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (issue_id) REFERENCES issues(id) ON DELETE CASCADE,
            FOREIGN KEY (assigned_by) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (assigned_to) REFERENCES users(id) ON DELETE CASCADE,
            INDEX (issue_id),
            INDEX (assigned_to)
        )
    """)
    db.commit()
    print("  ✓ issue_assignments table ready")
    
    # Check if verification_status column exists
    cursor.execute("SHOW COLUMNS FROM issues WHERE Field='verification_status'")
    if not cursor.fetchone():
        print("  Adding verification_status column...")
        cursor.execute("""
            ALTER TABLE issues 
            ADD COLUMN verification_status VARCHAR(50) DEFAULT 'Pending' AFTER resolved_at
        """)
        db.commit()
        print("  ✓ verification_status column added")
    else:
        print("  - verification_status column already exists")
    
    # Check if verified_by column exists
    cursor.execute("SHOW COLUMNS FROM issues WHERE Field='verified_by'")
    if not cursor.fetchone():
        print("  Adding verified_by column...")
        cursor.execute("""
            ALTER TABLE issues 
            ADD COLUMN verified_by INT AFTER verification_status,
            ADD FOREIGN KEY (verified_by) REFERENCES users(id) ON DELETE SET NULL
        """)
        db.commit()
        print("  ✓ verified_by column added")
    else:
        print("  - verified_by column already exists")
    
    # Create issue_resolutions table if it doesn't exist
    print("Creating issue_resolutions table if it doesn't exist...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS issue_resolutions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            issue_id INT NOT NULL,
            resolved_by INT NOT NULL,
            comments TEXT,
            image_path VARCHAR(255),
            resolution_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (issue_id) REFERENCES issues(id) ON DELETE CASCADE,
            FOREIGN KEY (resolved_by) REFERENCES users(id) ON DELETE CASCADE,
            INDEX (issue_id),
            INDEX (resolved_by)
        )
    """)
    db.commit()
    print("  ✓ issue_resolutions table ready")
    
    # Add indexes if they don't exist
    print("\nAdding indexes...")
    cursor.execute("SHOW INDEX FROM issues WHERE Column_name='assigned_to'")
    if not cursor.fetchone():
        cursor.execute("ALTER TABLE issues ADD INDEX idx_assigned_to (assigned_to)")
        db.commit()
        print("  ✓ Index on assigned_to added")
    else:
        print("  - Index on assigned_to already exists")
    
    cursor.execute("SHOW INDEX FROM issues WHERE Column_name='status'")
    if not cursor.fetchone():
        cursor.execute("ALTER TABLE issues ADD INDEX idx_status (status)")
        db.commit()
        print("  ✓ Index on status added")
    else:
        print("  - Index on status already exists")
    
    cursor.execute("SHOW INDEX FROM issues WHERE Column_name='verification_status'")
    if not cursor.fetchone():
        cursor.execute("ALTER TABLE issues ADD INDEX idx_verification_status (verification_status)")
        db.commit()
        print("  ✓ Index on verification_status added")
    else:
        print("  - Index on verification_status already exists")
    
    cursor.execute("SHOW INDEX FROM issues WHERE Column_name='verified_by'")
    if not cursor.fetchone():
        cursor.execute("ALTER TABLE issues ADD INDEX idx_verified_by (verified_by)")
        db.commit()
        print("  ✓ Index on verified_by added")
    else:
        print("  - Index on verified_by already exists")
    
    print("\n✓ Database setup complete!")
    cursor.close()
    db.close()
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
