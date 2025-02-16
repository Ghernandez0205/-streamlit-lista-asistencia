import os
import sqlite3

db_path = r"C:\\Users\\sup11\\OneDrive\\Attachments\\Documentos\\Interfaces de phyton\\Lista de asistencia\\asistencia.db"

# Verificar si la base de datos existe antes de conectarse
if not os.path.exists(db_path):
    raise FileNotFoundError(f"La base de datos no se encuentra en: {db_path}")

# Conexión a la base de datos
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Probar una consulta
try:
    cursor.execute("SELECT id, apellido_paterno, apellido_materno, nombre FROM docentes WHERE activo = 1")
    resultados = cursor.fetchall()
    print("Conexión exitosa. Se encontraron:", len(resultados), "docentes activos.")
except sqlite3.OperationalError as e:
    print("Error en la consulta SQL:", e)

conn.close()
