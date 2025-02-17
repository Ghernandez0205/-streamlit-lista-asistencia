import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Configuración de contraseña
PASSWORD = "supervision11"

# Conexión a la base de datos SQLite
DB_PATH = "C:/Users/sup11/OneDrive/Attachments/Documentos/Interfaces de phyton/Lista de asistencia/asistencia.db"

def crear_tabla():
    """ Crea la tabla de asistencia si no existe """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS asistencia (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            fecha TEXT NOT NULL,
            hora_entrada TEXT NOT NULL,
            hora_salida TEXT NOT NULL,
            actividad TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def obtener_docentes():
    """ Obtiene la lista de docentes activos desde la base de datos """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT nombre FROM docentes WHERE activo = 1")
    docentes = [row[0] for row in cursor.fetchall()]
    conn.close()
    return docentes

def registrar_asistencia(nombre, fecha, hora_entrada, hora_salida, actividad):
    """ Registra la asistencia en la base de datos """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO asistencia (nombre, fecha, hora_entrada, hora_salida, actividad) 
            VALUES (?, ?, ?, ?, ?)
        """, (nombre, fecha, hora_entrada, hora_salida, actividad))
        conn.commit()
        conn.close()
        st.success("Registro guardado exitosamente.")
    except sqlite3.Error as e:
        st.error(f"Error al registrar la asistencia: {e}")

# Verificación de contraseña
def verificar_contraseña():
    st.title("Inicio de Sesión")
    contraseña_ingresada = st.text_input("Ingrese la contraseña:", type="password")
    if st.button("Acceder"):
        if contraseña_ingresada == PASSWORD:
            st.session_state["autenticado"] = True
            st.rerun()
        else:
            st.error("Contraseña incorrecta.")

# Interfaz de Registro
def interfaz_registro():
    st.title("Registro de Asistencia")

    actividad = st.text_input("Ingrese el nombre de la actividad:")
    fecha = st.date_input("Seleccione la fecha de la actividad:", datetime.today())
    
    docentes = obtener_docentes()
    if not docentes:
        st.warning("No hay docentes disponibles.")
        return
    
    seleccionados = st.multiselect("Seleccione los docentes", docentes)
    
    hora_entrada = st.time_input("Hora de Entrada")
    hora_salida = st.time_input("Hora de Salida")

    if st.button("Registrar Asistencia"):
        if not seleccionados:
            st.warning("Seleccione al menos un docente.")
        else:
            for docente in seleccionados:
                registrar_asistencia(docente, fecha, hora_entrada, hora_salida, actividad)
            st.success("Asistencia registrada correctamente.")

# Ejecutar la app
crear_tabla()

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    verificar_contraseña()
else:
    interfaz_registro()

