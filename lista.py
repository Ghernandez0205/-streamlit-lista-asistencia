import streamlit as st
import sqlite3
import datetime
import pandas as pd
import shutil

# Función para obtener docentes activos desde SQLite
def obtener_docentes():
    conn = sqlite3.connect("asistencia.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, apellido_paterno, apellido_materno, nombre FROM docentes WHERE activo = 1")
    docentes = [{"id": row[0], "nombre_completo": f"{row[1]} {row[2]} {row[3]}"} for row in cursor.fetchall()]
    conn.close()
    return docentes

# Función para registrar asistencia en SQLite
def registrar_asistencia(nombre, fecha, hora_entrada, hora_salida, actividad):
    conn = sqlite3.connect("asistencia.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO asistencia (nombre, fecha, hora_entrada, hora_salida, actividad)
        VALUES (?, ?, ?, ?, ?)
    """, (nombre, fecha, hora_entrada, hora_salida, actividad))
    conn.commit()
    conn.close()

# Función para eliminar docentes (darlos de baja)
def eliminar_docente(docente_id):
    conn = sqlite3.connect("asistencia.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE docentes SET activo = 0 WHERE id = ?", (docente_id,))
    conn.commit()
    conn.close()

# Interfaz en Streamlit
st.title("Registro de Asistencia")

# Selección de actividad
actividad = st.text_input("Ingrese el nombre de la actividad:")
fecha_actividad = st.date_input("Seleccione la fecha de la actividad:")

# Lista de docentes desde SQLite
docentes = obtener_docentes()
if docentes:
    opciones = {docente["nombre_completo"]: docente["id"] for docente in docentes}
    docente_seleccionado = st.selectbox("Seleccione un docente:", opciones.keys())

    # Registro de horarios
    hora_entrada = st.time_input("Hora de Entrada:", value=datetime.datetime.now().time())
    hora_salida = st.time_input("Hora de Salida:", value=datetime.datetime.now().time())

    # Botón para registrar asistencia
    if st.button("Registrar Asistencia"):
        registrar_asistencia(docente_seleccionado, fecha_actividad, hora_entrada, hora_salida, actividad)
        st.success(f"Asistencia registrada para {docente_seleccionado}.")
    
    # Botón para eliminar docente
    if st.button("Dar de Baja al Docente"):
        eliminar_docente(opciones[docente_seleccionado])
        st.warning(f"El docente {docente_seleccionado} ha sido dado de baja.")

else:
    st.warning("No hay docentes registrados o todos están dados de baja.")

# Mostrar la lista de asistencia
st.subheader("Lista de Asistencia del día")
conn = sqlite3.connect("asistencia.db")
df_asistencia = pd.read_sql_query("SELECT * FROM asistencia", conn)
conn.close()
st.dataframe(df_asistencia)

# Guardar en OneDrive
onedrive_path = r"C:\\Users\\sup11\\OneDrive\\Attachments\\Documentos\\Interfaces de phyton\\Lista de asistencia"
if st.button("Guardar en OneDrive"):
    archivo_origen = "asistencia.xlsx"
    archivo_destino = f"{onedrive_path}\\asistencia.xlsx"
    shutil.copy(archivo_origen, archivo_destino)
    st.success("Asistencia guardada en OneDrive.")

# Exportar a Excel
if st.button("Exportar Asistencia a Excel"):
    df_asistencia.to_excel("asistencia.xlsx", index=False)
    st.success("Asistencia exportada a Excel correctamente.")
