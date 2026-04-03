import sqlite3
import os

# Check both potential database locations
locations = [
    os.path.join(os.path.dirname(__file__), "blog.db"),
    os.path.join(os.path.dirname(__file__), "instance", "blog.db"),
]

for db_path in locations:
    if os.path.exists(db_path):
        print(f"\n=== {db_path} ===")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [t[0] for t in cursor.fetchall()]
        print(f"Tables: {tables}")
        if "users" in tables:
            cursor.execute("SELECT id, username FROM users")
            print(f"Users: {cursor.fetchall()}")
        conn.close()
    else:
        print(f"\n{db_path} - NOT FOUND")
