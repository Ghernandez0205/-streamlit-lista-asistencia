import sqlite3

db_path = "C:/Users/sup11/OneDrive/Attachments/Documentos/Interfaces de phyton/Lista de asistencia/asistencia.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(asistencia);")
columns = cursor.fetchall()

for col in columns:
    print(col)

conn.close()
