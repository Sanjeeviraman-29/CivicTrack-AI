#!/usr/bin/env python3
"""
Automated database viewer - No MySQL CLI needed
Connects to MySQL and displays database contents
"""

import mysql.connector
from dotenv import load_dotenv
import os
from tabulate import tabulate

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), 'backend', '.env'))

def connect_db():
    """Connect to MySQL database"""
    try:
        db = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", "root"),
            database=os.getenv("DB_NAME", "civictrack_ai")
        )
        return db
    except mysql.connector.Error as err:
        print(f"❌ Connection Error: {err}")
        print("\nTroubleshooting:")
        print("1. Is MySQL running? (Services > MySQL80)")
        print("2. Check credentials in backend/.env")
        print("3. Does 'civictrack_ai' database exist?")
        return None

def show_tables(db):
    """List all tables"""
    cursor = db.cursor()
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    cursor.close()
    
    print("\n" + "="*50)
    print("📊 DATABASE TABLES")
    print("="*50)
    for table in tables:
        print(f"  • {table[0]}")
    return [t[0] for t in tables]

def show_table_data(db, table_name):
    """Show data from a specific table"""
    cursor = db.cursor()
    try:
        cursor.execute(f"SELECT * FROM {table_name}")
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        
        print(f"\n{'='*80}")
        print(f"📋 TABLE: {table_name.upper()} ({len(rows)} rows)")
        print('='*80)
        
        if rows:
            print(tabulate(rows, headers=columns, tablefmt="grid"))
        else:
            print("  (No data)")
        
        cursor.close()
        return True
    except Exception as e:
        print(f"  Error reading {table_name}: {e}")
        cursor.close()
        return False

def main():
    print("\n🔗 Connecting to database...")
    db = connect_db()
    
    if not db:
        print("\n❌ Could not connect. Starting application anyway...")
        return
    
    print("✅ Connected!")
    
    tables = show_tables(db)
    
    if not tables:
        print("\n⚠️  No tables found. Run setup_database.py first:")
        print("   python setup_database.py")
        db.close()
        return
    
    # Show data for each table
    for table in tables:
        show_table_data(db, table)
    
    db.close()
    print("\n" + "="*80)
    print("✅ Database view complete!\n")

if __name__ == "__main__":
    main()
