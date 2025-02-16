import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# Ruta de la base de datos
DB_PATH = "C:/Users/sup11/OneDrive/Attachments/Documentos/Interfaces de phyton/Lista de asistencia/asistencia.db"

# Función para obtener la lista de docentes activos
def obtener_docentes():
    try:
        conn = sqlite3.connect(DB_PATH)
        query = "SELECT id, apellido_paterno, apellido_materno, nombre FROM docentes WHERE activo = 1"
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error al obtener la lista de docentes: {e}")
        return pd.DataFrame()

# Función para registrar asistencia
def registrar_asistencia(docentes_seleccionados, hora_entrada, hora_salida, fecha_actividad):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        for docente_id in docentes_seleccionados:
            cursor.execute(
                """
                INSERT INTO asistencia (docente_id, fecha, hora_entrada, hora_salida) 
                VALUES (?, ?, ?, ?)
                """,
                (docente_id, fecha_actividad, hora_entrada, hora_salida)
            )
        
        conn.commit()
        conn.close()
        st.success("Registro de asistencia guardado exitosamente.")
    except Exception as e:
        st.error(f"Error al registrar la asistencia: {e}")

# Cargar docentes
docentes_df = obtener_docentes()

# UI en Streamlit
st.title("Registro de Asistencia")

# Selección de actividad y fecha
actividad = st.text_input("Ingrese la actividad:")
fecha_actividad = st.date_input("Seleccione la fecha de la actividad:", datetime.today())

# Selección de docentes múltiples
if not docentes_df.empty:
    docentes_df["nombre_completo"] = docentes_df["apellido_paterno"] + " " + docentes_df["apellido_materno"] + " " + docentes_df["nombre"]
    docentes_seleccionados = st.multiselect("Seleccione los docentes", docentes_df["nombre_completo"].tolist())

    # Selección de horario
    hora_entrada = st.time_input("Hora de Entrada")
    hora_salida = st.time_input("Hora de Salida")

    if st.button("Registrar Asistencia"):
        docentes_ids = docentes_df[docentes_df["nombre_completo"].isin(docentes_seleccionados)]["id"].tolist()
        registrar_asistencia(docentes_ids, hora_entrada.strftime("%H:%M:%S"), hora_salida.strftime("%H:%M:%S"), fecha_actividad)

# Mostrar asistencia registrada
st.subheader("Lista de Asistencia del Día")

try:
    conn = sqlite3.connect(DB_PATH)
    df_asistencia = pd.read_sql("SELECT * FROM asistencia", conn)
    conn.close()

    if not df_asistencia.empty:
        df_asistencia = df_asistencia.rename(columns={
            "id": "No.",
            "docente_id": "Nombre Completo",
            "fecha": "Fecha",
            "hora_entrada": "Hora de Entrada",
            "hora_salida": "Hora de Salida"
        })

        # ✅ Evitar nombres de columnas duplicados
        df_asistencia.columns = pd.io.parsers.ParserBase({'names': df_asistencia.columns})._maybe_dedup_names()
        
        st.dataframe(df_asistencia)
    else:
        st.write("No hay registros de asistencia aún.")
except Exception as e:
    st.error(f"Error al cargar la asistencia: {e}")
