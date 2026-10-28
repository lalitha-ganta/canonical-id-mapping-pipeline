
from src.database import get_connection

conn = get_connection()

cursor = conn.cursor()

cursor.execute("""
    SELECT name
    FROM sqlite_master
    WHERE type = 'table'
    ORDER BY name
""")

tables = cursor.fetchall()

print("Tables available in our database:")

for table in tables:
    print(table[0])

print("Total tables:", len(tables))

conn.close()
