import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# 📌 Ruta de la base de datos en OneDrive
db_path = "C:/Users/sup11/OneDrive/Attachments/Documentos/Interfaces de phyton/Lista de asistencia/asistencia.db"

# 🔐 Contraseña requerida para acceder a la aplicación
PASSWORD = "supervision11"

# ✅ Función para verificar autenticación
def verificar_contraseña():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False

    if not st.session_state.autenticado:
        contraseña_ingresada = st.text_input("Ingrese la contraseña:", type="password")
        if st.button("Acceder"):
            if contraseña_ingresada == PASSWORD:
                st.session_state.autenticado = True
                st.experimental_rerun()
            else:
                st.error("Contraseña incorrecta.")

# 📌 Función para obtener docentes activos desde la base de datos
def obtener_docentes():
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, apellido_paterno, apellido_materno, nombre FROM docentes WHERE activo = 1")
        docentes = cursor.fetchall()
        conn.close()
        return [(f"{doc[1]} {doc[2]} {doc[3]}", doc[0]) for doc in docentes]  # Nombre completo y ID
    except Exception as e:
        st.error(f"Error al obtener docentes: {e}")
        return []

# 📌 Función para registrar asistencia en la base de datos
def registrar_asistencia(docente_id, nombre, fecha, hora_entrada, hora_salida, actividad):
    try:
        if not nombre or nombre.strip() == "":
            st.error("Debe seleccionar un docente antes de registrar la asistencia.")
            return

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        query = """INSERT INTO asistencia (docente_id, nombre, fecha, hora_entrada, hora_salida, actividad) 
                   VALUES (?, ?, ?, ?, ?, ?)"""
        cursor.execute(query, (docente_id, nombre, fecha, hora_entrada, hora_salida, actividad))
        conn.commit()
        conn.close()

        st.success(f"Asistencia registrada correctamente para {nombre}")

    except Exception as e:
        st.error(f"Error al registrar la asistencia: {e}")

# 🔑 Verificar autenticación antes de mostrar la interfaz
verificar_contraseña()

# 🚀 Solo mostrar la interfaz si el usuario está autenticado
if st.session_state.autenticado:
    st.title("Registro de Asistencia")

    # 📌 Captura de actividad y fecha
    actividad = st.text_input("Ingrese el nombre de la actividad:", "")
    fecha = st.date_input("Seleccione la fecha de la actividad:", datetime.today())

    # 📌 Selección de docente
    docentes = obtener_docentes()
    if docentes:
        docente_seleccionado = st.selectbox("Seleccione el Docente:", [d[0] for d in docentes])
        docente_id = next((d[1] for d in docentes if d[0] == docente_seleccionado), None)
    else:
        st.error("No hay docentes disponibles.")
        docente_id = None

    # 📌 Selección de horario
    hora_entrada = st.time_input("Hora de Entrada:", value=datetime.now().time())
    hora_salida = st.time_input("Hora de Salida:", value=datetime.now().time())

    # 📌 Botón para registrar asistencia
    if st.button("Registrar Asistencia"):
        if docente_id:
            registrar_asistencia(docente_id, docente_seleccionado, fecha, hora_entrada, hora_salida, actividad)
        else:
            st.error("Seleccione un docente antes de continuar.")

    # 📌 Mostrar lista de asistencia del día
    st.subheader("Lista de Asistencia del día")
    try:
        conn = sqlite3.connect(db_path)
        df_asistencia = pd.read_sql_query("SELECT nombre, fecha, hora_entrada, hora_salida, actividad FROM asistencia WHERE fecha = ?", conn, params=(fecha,))
        conn.close()
        st.dataframe(df_asistencia)
    except Exception as e:
        st.error(f"Error al cargar la lista de asistencia: {e}")
