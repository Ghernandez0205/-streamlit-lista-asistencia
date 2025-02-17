import sqlite3

# Ruta de la base de datos
db_path = "C:/Users/sup11/OneDrive/Attachments/Documentos/Interfaces de phyton/Lista de asistencia/asistencia.db"

# Conectar con la base de datos
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Agregar la columna docente_id si no existe
try:
    cursor.execute("ALTER TABLE asistencia ADD COLUMN docente_id INTEGER;")
    conn.commit()
    print("Columna 'docente_id' agregada correctamente.")
except sqlite3.OperationalError:
    print("La columna 'docente_id' ya existe o no es necesario agregarla.")

# Cerrar la conexión
conn.close()
