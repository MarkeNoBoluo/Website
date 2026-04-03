import sqlite3

conn = sqlite3.connect("blog.db")
cursor = conn.cursor()
cursor.execute("SELECT id, title, status, slug FROM articles")
articles = cursor.fetchall()
print("Articles in database:")
for a in articles:
    print(f"  ID={a[0]}, title={a[1]}, status={a[2]}, slug={a[3]}")
conn.close()
