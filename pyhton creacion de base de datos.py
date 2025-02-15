import sqlite3
import pandas as pd

# Ruta del archivo SQLite
db_path = "asistencia.db"

# Conectar con la base de datos
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Crear la tabla de docentes
cursor.execute("""
    CREATE TABLE IF NOT EXISTS docentes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        apellido_paterno TEXT NOT NULL,
        apellido_materno TEXT NOT NULL,
        nombre TEXT NOT NULL,
        activo INTEGER DEFAULT 1
    )
""")

# Cargar docentes desde el archivo PLANTILLA.xlsx
ruta_excel = "PLANTILLA.xlsx"
df = pd.read_excel(ruta_excel, engine='openpyxl')

# Verificar si las columnas existen en el archivo Excel
columnas_esperadas = ["APELLIDO PATERNO", "APELLIDO MATERNO", "NOMBRE (S)"]
if all(col in df.columns for col in columnas_esperadas):
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT OR IGNORE INTO docentes (apellido_paterno, apellido_materno, nombre)
            VALUES (?, ?, ?)
        """, (row["APELLIDO PATERNO"], row["APELLIDO MATERNO"], row["NOMBRE (S)"]))

    conn.commit()
    print("Docentes importados correctamente en la base de datos.")
else:
    print("Error: Las columnas del archivo Excel no coinciden.")

# Cerrar conexión
conn.close()
