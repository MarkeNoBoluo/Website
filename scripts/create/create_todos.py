import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), "instance", "blog.db")
print(f"Connecting to: {db_path}")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check current tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in cursor.fetchall()]
print(f"Current tables: {tables}")

# Create todos table if not exists
if "todos" not in tables:
    print("Creating todos table...")
    cursor.execute("""
        CREATE TABLE todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title VARCHAR(200) NOT NULL,
            description TEXT,
            quadrant INTEGER NOT NULL,
            priority INTEGER DEFAULT 3,
            due_date DATETIME,
            completed BOOLEAN DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            CHECK (quadrant IN (1, 2, 3, 4)),
            CHECK (priority IN (1, 2, 3, 4, 5)),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    conn.commit()
    print("todos table created.")
else:
    print("todos table already exists.")

# Verify
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in cursor.fetchall()]
print(f"Tables after: {tables}")
conn.close()
print("Done.")
