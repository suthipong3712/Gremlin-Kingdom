from database import get_connection

conn = get_connection()

cursor = conn.cursor()

cursor.execute("""
INSERT INTO characters
(name,title,race,age,description,image)

VALUES

(
'King Gremlin',
'Second King',
'Gremlin',
120,
'The second king of Gremlin Kingdom.',
'gremlin.png'
)
""")

conn.commit()

conn.close()

print("Character Added!")