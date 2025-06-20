import sqlite3

# Connect to the database file
conn = sqlite3.connect("secondhand.db")  # We're already inside the 'database' folder
cursor = conn.cursor()

# Show tables in the database
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("✅ Tables in the database:")
for table in tables:
    print(" -", table[0])

# Optional: Check the schema of the Post table
print("\n📋 Structure of 'Post' table (if exists):")
cursor.execute("PRAGMA table_info(Post);")
columns = cursor.fetchall()
for column in columns:
    print(column)

conn.close()
