import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), "instance", "blog.db")
print(f"Fixing database: {db_path}")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check current tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in cursor.fetchall()]
print(f"Current tables: {tables}")

# Create users table if not exists
if "users" not in tables:
    print("Creating users table...")
    cursor.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(64) UNIQUE NOT NULL,
            password_hash VARCHAR(128) NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    print("users table created.")
else:
    print("users table already exists.")

# Create articles table if not exists
if "articles" not in tables:
    print("Creating articles table...")
    cursor.execute("""
        CREATE TABLE articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title VARCHAR(200) NOT NULL,
            content TEXT NOT NULL,
            slug VARCHAR(200) UNIQUE NOT NULL,
            status VARCHAR(20) DEFAULT 'draft',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            CHECK (status IN ('draft', 'published'))
        )
    """)
    conn.commit()
    print("articles table created.")
else:
    print("articles table already exists.")

# Verify final state
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in cursor.fetchall()]
print(f"Final tables: {tables}")
conn.close()
print("Done.")
