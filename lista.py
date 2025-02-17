import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta

# Configuración de la contraseña
PASSWORD = "defvm11"

# Ruta de la base de datos SQLite
DB_PATH = r"C:\Users\sup11\OneDrive\Attachments\Documentos\Interfaces de phyton\Lista de asistencia\asistencia.db"

# Función para crear la base de datos si no existe
def inicializar_bd():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Crear tabla de docentes si no existe
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS docentes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            apellido_paterno TEXT NOT NULL,
            apellido_materno TEXT NOT NULL,
            nombre TEXT NOT NULL,
            activo INTEGER DEFAULT 1
        )
    """)

    # Crear tabla de asistencia con columnas adicionales
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS asistencia (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            fecha TEXT NOT NULL,
            hora_entrada TEXT NOT NULL,
            firma_entrada TEXT DEFAULT '',
            hora_salida TEXT NOT NULL,
            firma_salida TEXT DEFAULT '',
            actividad TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()

# Función para obtener la lista de docentes activos
def obtener_docentes():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, apellido_paterno, apellido_materno, nombre FROM docentes WHERE activo = 1")
    docentes = cursor.fetchall()
    conn.close()
    return [f"{d[1]} {d[2]} {d[3]}" for d in docentes]

# Función para registrar asistencia
def registrar_asistencia(docentes, fecha, hora_entrada, hora_salida, actividad):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Registrar cada docente con horario escalonado
        for i, docente in enumerate(docentes):
            entrada_escalonada = (datetime.strptime(hora_entrada, "%H:%M") + timedelta(minutes=i)).strftime("%H:%M")
            cursor.execute("""
                INSERT INTO asistencia (nombre, fecha, hora_entrada, hora_salida, actividad) 
                VALUES (?, ?, ?, ?, ?)
            """, (docente, fecha, entrada_escalonada, hora_salida, actividad))

        conn.commit()
        st.success("Asistencia registrada correctamente.")
    except Exception as e:
        st.error(f"Error al registrar la asistencia: {e}")
    finally:
        conn.close()

# Verificación de contraseña
def verificar_contraseña():
    st.title("Sistema de Registro de Asistencia")
    password_input = st.text_input("Ingrese la contraseña:", type="password")
    if st.button("Acceder"):
        if password_input == PASSWORD:
            st.session_state["acceso"] = True
            st.experimental_rerun()
        else:
            st.error("Contraseña incorrecta.")

# UI de la aplicación
def main():
    inicializar_bd()
    
    if "acceso" not in st.session_state:
        verificar_contraseña()
        return

    st.title("Registro de Asistencia")

    fecha = st.date_input("Seleccione la fecha de la actividad:", datetime.today())
    actividad = st.text_input("Actividad:")
    docentes_seleccionados = st.multiselect("Seleccione el(los) Docente(s):", obtener_docentes())

    col1, col2 = st.columns(2)
    with col1:
        hora_entrada = st.time_input("Hora de Entrada:")
    with col2:
        hora_salida = st.time_input("Hora de Salida:")

    if st.button("Registrar Asistencia"):
        if docentes_seleccionados and actividad:
            registrar_asistencia(docentes_seleccionados, fecha.strftime("%Y-%m-%d"), hora_entrada.strftime("%H:%M"), hora_salida.strftime("%H:%M"), actividad)
        else:
            st.error("Debe seleccionar al menos un docente y escribir la actividad.")

    # Mostrar registros de asistencia
    st.subheader("Registros de Asistencia")
    try:
        conn = sqlite3.connect(DB_PATH)
        df_asistencia = pd.read_sql_query("SELECT id AS 'No.', nombre AS 'Nombre del Docente', hora_entrada AS 'Hora de Entrada', firma_entrada AS 'Firma Entrada', hora_salida AS 'Hora de Salida', firma_salida AS 'Firma Salida', fecha, actividad FROM asistencia", conn)
        conn.close()
        st.dataframe(df_asistencia)
    except Exception as e:
        st.error(f"Error al cargar los registros: {e}")

if __name__ == "__main__":
    main()
