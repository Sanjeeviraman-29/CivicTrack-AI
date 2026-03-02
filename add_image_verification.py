import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

# Connect to database
try:
    db = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )
    cursor = db.cursor(buffered=True)
    print("✓ Connected to database")
except Exception as e:
    print(f"✗ Connection error: {e}")
    exit(1)

# 1. Add columns to issues table for verification status
print("\n1. Adding verification columns to issues table...")
try:
    cursor.execute("ALTER TABLE issues ADD COLUMN verification_status VARCHAR(50) DEFAULT 'Pending' AFTER resolved_at")
    print("   ✓ Added verification_status column")
except mysql.connector.Error as e:
    if "Duplicate column" in str(e):
        print("   ! verification_status column already exists")
    else:
        print(f"   ✗ Error: {e}")

try:
    cursor.execute("ALTER TABLE issues ADD COLUMN verified_by INT AFTER verification_status")
    print("   ✓ Added verified_by column")
except mysql.connector.Error as e:
    if "Duplicate column" in str(e):
        print("   ! verified_by column already exists")
    else:
        print(f"   ✗ Error: {e}")

# 2. Add image_path to issue_resolutions table
print("\n2. Adding image storage to issue_resolutions table...")
try:
    cursor.execute("ALTER TABLE issue_resolutions ADD COLUMN image_path VARCHAR(255) AFTER comments")
    print("   ✓ Added image_path column")
except mysql.connector.Error as e:
    if "Duplicate column" in str(e):
        print("   ! image_path column already exists")
    else:
        print(f"   ✗ Error: {e}")

# 3. Add verification_date to issue_resolutions
try:
    cursor.execute("ALTER TABLE issue_resolutions ADD COLUMN verification_date TIMESTAMP AFTER image_path")
    print("   ✓ Added verification_date column")
except mysql.connector.Error as e:
    if "Duplicate column" in str(e):
        print("   ! verification_date column already exists")
    else:
        print(f"   ✗ Error: {e}")

# 4. Create verification_history table to track verification actions
print("\n3. Creating verification_history table...")
try:
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS verification_history (
        id INT AUTO_INCREMENT PRIMARY KEY,
        issue_id INT NOT NULL,
        verified_by INT NOT NULL,
        action VARCHAR(20) NOT NULL,
        reason VARCHAR(255),
        verification_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (issue_id) REFERENCES issues(id),
        FOREIGN KEY (verified_by) REFERENCES users(id)
    )
    """)
    print("   ✓ verification_history table created")
except Exception as e:
    print(f"   ✗ Error: {e}")

# 5. Create uploads directory if it doesn't exist
uploads_dir = "uploads"
if not os.path.exists(uploads_dir):
    os.makedirs(uploads_dir)
    print(f"\n4. Created '{uploads_dir}' directory for image storage")
else:
    print(f"\n4. '{uploads_dir}' directory already exists")

db.commit()
cursor.close()
db.close()

print("\n✓ Database migration completed successfully!")
print("⚠ Note: Create an 'uploads' folder in the project root if it doesn't exist")
