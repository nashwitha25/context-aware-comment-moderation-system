from db import get_db_connection

conn = get_db_connection()
cursor = conn.cursor()

cursor.execute("SHOW TABLES;")
tables = cursor.fetchall()

print("Connected! Tables:")
for t in tables:
    print(t)

conn.close()
