import sqlite3
import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Ruta de la base de datos SQLite y el archivo de Excel en OneDrive
DB_PATH = "C:/Users/sup11/OneDrive/Attachments/Documentos/Interfaces de phyton/Lista de asistencia/asistencia.db"
EXCEL_PATH = "C:/Users/sup11/OneDrive/Attachments/Documentos/Interfaces de phyton/Lista de asistencia/asistencia.xlsx"

# Conexión a la base de datos SQLite
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

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

# Selección de horas con conversión a string
hora_entrada = st.time_input("⏰ Hora de Entrada").strftime("%H:%M:%S")
hora_salida = st.time_input("⏳ Hora de Salida").strftime("%H:%M:%S")

actividad = st.text_input("📌 Actividad")

# Función para registrar asistencia
def registrar_asistencia(nombre, fecha, hora_entrada, hora_salida, actividad):
    try:
        cursor.execute(
            "INSERT INTO asistencia (nombre, fecha, hora_entrada, hora_salida, actividad) VALUES (?, ?, ?, ?, ?)",
            (nombre, fecha, hora_entrada, hora_salida, actividad),
        )
        conn.commit()
        
        # Guardar en Excel
        guardar_en_excel(nombre, fecha, hora_entrada, hora_salida, actividad)
        
        st.success("✅ Asistencia registrada correctamente.")
    except Exception as e:
        st.error(f"❌ Error al registrar la asistencia: {e}")

# Función para guardar en Excel
def guardar_en_excel(nombre, fecha, hora_entrada, hora_salida, actividad):
    # Verificar si el archivo ya existe
    if os.path.exists(EXCEL_PATH):
        df = pd.read_excel(EXCEL_PATH)
    else:
        df = pd.DataFrame(columns=["Nombre", "Fecha", "Hora Entrada", "Hora Salida", "Actividad"])

    # Crear un nuevo registro
    nuevo_registro = pd.DataFrame([[nombre, fecha, hora_entrada, hora_salida, actividad]],
                                  columns=["Nombre", "Fecha", "Hora Entrada", "Hora Salida", "Actividad"])

    # Agregar el nuevo registro al DataFrame
    df = pd.concat([df, nuevo_registro], ignore_index=True)

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
df_asistencia = pd.read_sql_query("SELECT * FROM asistencia", conn)
st.dataframe(df_asistencia)

# Cerrar la conexión
conn.close()
