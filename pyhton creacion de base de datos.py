import streamlit as st
import sqlite3
import pandas as pd
import datetime

# Ruta de la base de datos
db_path = r"C:\Users\sup11\OneDrive\Attachments\Documentos\Interfaces de phyton\Lista de asistencia\asistencia.db"

# Función para registrar asistencia en SQLite
def registrar_asistencia(nombre, fecha, hora_entrada, hora_salida, actividad):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Insertar datos en la tabla
        cursor.execute("""
            INSERT INTO asistencia (nombre, fecha, hora_entrada, hora_salida, actividad)
            VALUES (?, ?, ?, ?, ?)
        """, (nombre, fecha, hora_entrada, hora_salida, actividad))
        
        conn.commit()
        st.success(f"✅ Asistencia registrada para {nombre}.")
    except sqlite3.Error as e:
        st.error(f"❌ Error al registrar asistencia: {e}")
    finally:
        conn.close()

# Interfaz en Streamlit
st.title("Registro de Asistencia")

# Selección de actividad
actividad = st.text_input("Ingrese el nombre de la actividad:")
fecha_actividad = st.date_input("Seleccione la fecha de la actividad:")

# Ingreso del nombre
nombre_docente = st.text_input("Ingrese el nombre del docente:")

# Registro de horarios con solo horas y minutos
hora_entrada = st.time_input("Hora de Entrada:", value=datetime.datetime.now().replace(second=0, microsecond=0).time())
hora_salida = st.time_input("Hora de Salida:", value=datetime.datetime.now().replace(second=0, microsecond=0).time())

# Botón para registrar asistencia
if st.button("Registrar Asistencia"):
    if not actividad or not nombre_docente:
        st.warning("⚠️ Debe ingresar el nombre del docente y la actividad.")
    else:
        registrar_asistencia(
            nombre_docente, 
            fecha_actividad.strftime("%Y-%m-%d"), 
            hora_entrada.strftime("%H:%M"), 
            hora_salida.strftime("%H:%M"), 
            actividad
        )

# Mostrar la lista de asistencia
st.subheader("Lista de Asistencia del día")
conn = sqlite3.connect(db_path)
df_asistencia = pd.read_sql_query("SELECT * FROM asistencia", conn)
conn.close()

# Verificar si la tabla tiene datos
if not df_asistencia.empty:
    st.dataframe(df_asistencia)
else:
    st.warning("⚠️ No hay registros de asistencia en la base de datos.")
