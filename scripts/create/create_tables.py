import sqlite3

conn = sqlite3.connect("blog.db")
cursor = conn.cursor()

# Create todos table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS todos (
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

# Create articles table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS articles (
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

# Verify
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in cursor.fetchall()]
print("Tables:", tables)
conn.close()
print("Done.")
