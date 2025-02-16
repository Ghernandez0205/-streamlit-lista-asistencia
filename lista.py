import streamlit as st
import pandas as pd
import sqlite3
import datetime
import os
from io import BytesIO

# Configuración de la contraseña
PASSWORD = "defvm11"

# Estado de autenticación
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Página de inicio de sesión
if not st.session_state.authenticated:
    st.title("🔐 Sistema de Registro de Asistencia")
    password_input = st.text_input("Ingrese la contraseña:", type="password")
    if st.button("Ingresar"):
        if password_input == PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("⚠️ Contraseña incorrecta")
    st.stop()

# **📌 Rutas**
DB_PATH = r"C:\Users\sup11\OneDrive\Attachments\Documentos\Interfaces de phyton\Lista de asistencia\asistencia.db"
ONEDRIVE_PATH = r"C:\Users\sup11\OneDrive\Attachments\Documentos\Interfaces de phyton\Lista de asistencia\Listas de asistencia"

# Crear carpeta en OneDrive si no existe
if not os.path.exists(ONEDRIVE_PATH):
    os.makedirs(ONEDRIVE_PATH)

# **📌 Función para obtener docentes desde SQLite**
def obtener_docentes():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, apellido_paterno, apellido_materno, nombre FROM docentes WHERE activo = 1")
    docentes = cursor.fetchall()
    conn.close()
    return {f"{d[1]} {d[2]} {d[3]}": d[0] for d in docentes}

# **📌 Obtener lista de docentes**
docentes = obtener_docentes()

# **📌 Registro de actividad**
st.title("📋 Registro de Actividad")
actividad = st.text_input("Ingrese el nombre de la actividad:")
fecha_actividad = st.date_input("Seleccione la fecha de la actividad:")

if not actividad or not fecha_actividad:
    st.warning("⚠️ Debe ingresar la actividad y la fecha antes de continuar.")
    st.stop()

# **📌 Nombre del archivo de asistencia**
nombre_archivo = f"Asistencia_{actividad}_{fecha_actividad}.xlsx"
archivo_ruta = os.path.join(ONEDRIVE_PATH, nombre_archivo)

# **📌 Inicializar DataFrame**
columnas = ["Nombre", "Hora de Entrada", "Hora de Salida"]
if os.path.exists(archivo_ruta):
    df_asistencia = pd.read_excel(archivo_ruta, engine='openpyxl')
else:
    df_asistencia = pd.DataFrame(columns=columnas)

# **📌 Formulario de registro de asistencia**
st.title("📌 Registro de Asistencia")
nombre_docente = st.selectbox("Seleccione un docente:", options=docentes.keys())

# **⏰ Selección de horarios**
hora_entrada = st.time_input("🕒 Hora de Entrada:", value=datetime.datetime.now().time())
hora_salida = st.time_input("🕒 Hora de Salida:", value=datetime.datetime.now().time())

# **📌 Función para registrar asistencia en SQLite**
def registrar_asistencia(nombre, fecha, hora_entrada, hora_salida, actividad):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        IN
