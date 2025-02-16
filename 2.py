import sqlite3  # Asegura que sqlite3 esté importado

# Ruta de la base de datos en OneDrive
db_path = r"C:\Users\sup11\OneDrive\Attachments\Documentos\Interfaces de phyton\Lista de asistencia\asistencia.db"

# Conectar a la base de datos
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Crear la tabla si no existe
cursor.execute("""
    CREATE TABLE IF NOT EXISTS asistencia (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        fecha DATE NOT NULL,
        hora_entrada TIME NOT NULL,
        hora_salida TIME NOT NULL,
        actividad TEXT NOT NULL
    )
""")

conn.commit()
conn.close()
print("✅ La base de datos y la tabla 'asistencia' han sido creadas correctamente.")
