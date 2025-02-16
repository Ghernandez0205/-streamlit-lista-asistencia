import sqlite3

# Ruta de la base de datos
db_path = r"C:\Users\sup11\OneDrive\Attachments\Documentos\Interfaces de phyton\Lista de asistencia\asistencia.db"

# Conectar a la base de datos
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Verificar si la tabla asistencia existe
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='asistencia'")
tabla_existente = cursor.fetchone()

if tabla_existente:
    print("✅ La tabla 'asistencia' existe en la base de datos.")
else:
    print("❌ La tabla 'asistencia' NO existe. Debes crearla.")

conn.close()
