from database import get_connection
conn = get_connection()
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS characters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    title TEXT,
    race TEXT,
    age INTEGER,
    description TEXT,
    image TEXT
)  
""")

conn.commit()
conn.close()
print("Database Created Successfully")