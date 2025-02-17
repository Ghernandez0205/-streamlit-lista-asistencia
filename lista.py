import sqlite3
import streamlit as st
from datetime import datetime

# Conexión a la base de datos
DB_PATH = "C:/Users/sup11/OneDrive/Attachments/Documentos/Interfaces de phyton/Lista de asistencia/asistencia.db"
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Función para registrar asistencia
def registrar_asistencia(nombre, fecha, hora_entrada, hora_salida, actividad):
    try:
        # Convertir hora a formato string para que SQLite lo acepte
        hora_entrada_str = hora_entrada.strftime("%H:%M:%S")
        hora_salida_str = hora_salida.strftime("%H:%M:%S")

        cursor.execute(
            "INSERT INTO asistencia (nombre, fecha, hora_entrada, hora_salida, actividad) VALUES (?, ?, ?, ?, ?)",
            (nombre, fecha, hora_entrada_str, hora_salida_str, actividad),
        )
        conn.commit()
        st.success("Asistencia registrada correctamente.")
    except Exception as e:
        st.error(f"Error al registrar la asistencia: {e}")

# Interfaz en Streamlit
st.title("Registro de Asistencia")

nombre = st.text_input("Nombre del docente")
fecha = st.date_input("Fecha de asistencia", datetime.today())

# Selección de horas convertidas a datetime.time
hora_entrada = st.time_input("Hora de Entrada")
hora_salida = st.time_input("Hora de Salida")

actividad = st.text_input("Actividad")

if st.button("Registrar Asistencia"):
    registrar_asistencia(nombre, fecha, hora_entrada, hora_salida, actividad)

# Cerrar la conexión a la base de datos al finalizar
conn.close()

