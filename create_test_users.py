#!/usr/bin/env python3
"""
Create test users for the system
"""

import mysql.connector
from dotenv import load_dotenv
import os
import bcrypt

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
    
    # Check for admin user
    cursor.execute("SELECT * FROM users WHERE role='admin' LIMIT 1")
    admin = cursor.fetchone()
    
    if not admin:
        print("Creating admin user...")
        password = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute(
            "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)",
            ("Admin User", "admin@example.com", password, "admin")
        )
        db.commit()
        print("✓ Admin user created (admin@example.com / admin123)\n")
    else:
        print(f"✓ Admin user already exists: {admin[2]}\n")
    
    # Check for resolver user
    cursor.execute("SELECT * FROM users WHERE role='resolver' LIMIT 1")
    resolver = cursor.fetchone()
    
    if not resolver:
        print("Creating resolver user...")
        password = bcrypt.hashpw("resolver123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute(
            "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)",
            ("John Resolver", "resolver@example.com", password, "resolver")
        )
        db.commit()
        print("✓ Resolver user created (resolver@example.com / resolver123)\n")
    else:
        print(f"✓ Resolver user already exists: {resolver[2]}\n")
    
    # Check for citizen user
    cursor.execute("SELECT * FROM users WHERE role='citizen' LIMIT 1")
    citizen = cursor.fetchone()
    
    if not citizen:
        print("Creating citizen user...")
        password = bcrypt.hashpw("citizen123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute(
            "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)",
            ("Jane Citizen", "citizen@example.com", password, "citizen")
        )
        db.commit()
        print("✓ Citizen user created (citizen@example.com / citizen123)\n")
    else:
        print(f"✓ Citizen user already exists: {citizen[2]}\n")
    
    # Show all users
    print("Current users in database:")
    cursor.execute("SELECT id, name, email, role FROM users")
    users = cursor.fetchall()
    for user in users:
        print(f"  - {user[1]} ({user[3]}): {user[2]}")
    
    cursor.close()
    db.close()
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
