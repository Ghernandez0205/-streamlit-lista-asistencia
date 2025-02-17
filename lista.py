import sqlite3
import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Ruta de la base de datos SQLite y el archivo de Excel en OneDrive
DB_PATH = "C:/Users/sup11/OneDrive/Attachments/Documentos/Interfaces de phyton/Lista de asistencia/asistencia.db"
EXCEL_PATH = "C:/Users/sup11/OneDrive/Attachments/Documentos/Interfaces de phyton/Lista de asistencia/asistencia.xlsx"

# Conexión a la base de datos SQLite
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()

# Verificar y agregar columnas faltantes en la base de datos
cursor.execute("""
CREATE TABLE IF NOT EXISTS asistencia (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    hora_entrada TEXT NOT NULL,
    firma_entrada TEXT DEFAULT 'Pendiente',
    hora_salida TEXT NOT NULL,
    firma_salida TEXT DEFAULT 'Pendiente',
    fecha TEXT NOT NULL,
    actividad TEXT NOT NULL
)
""")
conn.commit()

# Función para verificar la contraseña
def verificar_contraseña(contraseña_ingresada):
    return contraseña_ingresada == "defvm11"

# Interfaz de autenticación
st.title("🔐 Acceso al Registro de Asistencia")
contraseña = st.text_input("Ingrese la contraseña:", type="password")
if not verificar_contraseña(contraseña):
    st.error("❌ Contraseña incorrecta. Intente nuevamente.")
    st.stop()

st.success("✅ Acceso concedido. Puede registrar asistencia.")

# Interfaz de Registro de Asistencia
st.header("📌 Registro de Asistencia")

nombre = st.text_input("👨‍🏫 Nombre del docente")
fecha = st.date_input("📅 Fecha de asistencia", datetime.today())

# Selección de actividad
actividad = st.text_input("📝 Actividad realizada")

# Selección de horas con conversión a string
hora_entrada = st.time_input("⏰ Hora de Entrada").strftime("%H:%M:%S")
hora_salida = st.time_input("⏳ Hora de Salida").strftime("%H:%M:%S")

# Función para registrar asistencia
def registrar_asistencia(nombre, fecha, hora_entrada, hora_salida, actividad):
    try:
        cursor.execute(
            "INSERT INTO asistencia (nombre, hora_entrada, hora_salida, fecha, actividad) VALUES (?, ?, ?, ?, ?)",
            (nombre, hora_entrada, hora_salida, fecha, actividad),
        )
        conn.commit()
        
        # Guardar en Excel
        guardar_en_excel()
        
        st.success("✅ Asistencia registrada correctamente.")
    except Exception as e:
        st.error(f"❌ Error al registrar la asistencia: {e}")

# Función para guardar en Excel
def guardar_en_excel():
    df = pd.read_sql_query("SELECT id AS 'No.', nombre AS 'Nombre del Docente', hora_entrada AS 'Hora de Entrada', firma_entrada AS 'Firma Entrada', hora_salida AS 'Hora de Salida', firma_salida AS 'Firma Salida', fecha, actividad FROM asistencia", conn)
    
    # Guardar en Excel
    df.to_excel(EXCEL_PATH, index=False)
    st.success("✅ Registro guardado en Excel en OneDrive.")

# Botón para registrar asistencia
if st.button("Registrar Asistencia"):
    if nombre and actividad:
        registrar_asistencia(nombre, fecha, hora_entrada, hora_salida, actividad)
    else:
        st.error("❌ Debe completar todos los campos antes de registrar la asistencia.")

# Mostrar registros en la interfaz
st.header("📄 Registros de Asistencia")
df_asistencia = pd.read_sql_query("SELECT id AS 'No.', nombre AS 'Nombre del Docente', hora_entrada AS 'Hora de Entrada', firma_entrada AS 'Firma Entrada', hora_salida AS 'Hora de Salida', firma_salida AS 'Firma Salida', fecha, actividad FROM asistencia", conn)
st.dataframe(df_asistencia)

# Cerrar la conexión
conn.close()
