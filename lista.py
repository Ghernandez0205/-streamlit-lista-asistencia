import streamlit as st
import pandas as pd
import sqlite3
import datetime
import os
from io import BytesIO

# 🔹 Configuración de la contraseña
PASSWORD = "defvm11"

# 🔹 Estado de autenticación
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# 🔹 Página de inicio de sesión
if not st.session_state.authenticated:
    st.title("Sistema de Registro de Asistencia")
    password_input = st.text_input("Ingrese la contraseña:", type="password")
    if st.button("Ingresar"):
        if password_input == PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Contraseña incorrecta")
    st.stop()

# 🔹 Ruta de la base de datos SQLite
DB_PATH = r"C:\\Users\\sup11\\OneDrive\\Attachments\\Documentos\\Interfaces de phyton\\Lista de asistencia\\asistencia.db"

# 🔹 Verificar si la base de datos existe antes de conectarse
if not os.path.exists(DB_PATH):
    st.error(f"La base de datos no se encuentra en: {DB_PATH}")
    st.stop()

# 🔹 Conexión a la base de datos
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 🔹 Obtener la lista de docentes desde la base de datos
def obtener_docentes():
    try:
        cursor.execute("SELECT id, apellido_paterno, apellido_materno, nombre FROM docentes WHERE activo = 1")
        return cursor.fetchall()
    except sqlite3.OperationalError as e:
        st.error(f"Error en la consulta SQL: {e}")
        return []

docentes = obtener_docentes()

# 🔹 Directorio en OneDrive para guardar listas de asistencia
ONEDRIVE_PATH = r"C:\\Users\\sup11\\OneDrive\\Attachments\\Documentos\\Interfaces de phyton\\Lista de asistencia\\Listas de asistencia"
if not os.path.exists(ONEDRIVE_PATH):
    os.makedirs(ONEDRIVE_PATH)

# 🔹 Registro de actividad y fecha
st.title("Registro de Actividad")
actividad = st.text_input("Ingrese el nombre de la actividad:")
fecha_actividad = st.date_input("Seleccione la fecha de la actividad:")

if not actividad or not fecha_actividad:
    st.warning("Debe ingresar la actividad y la fecha antes de continuar.")
    st.stop()

# 🔹 Nombre del archivo de asistencia en OneDrive
nombre_archivo = f"Asistencia_{actividad}_{fecha_actividad}.xlsx"
archivo_ruta = os.path.join(ONEDRIVE_PATH, nombre_archivo)

# 🔹 Inicializar dataframe de asistencia
columnas = ["Nombre", "Hora de Entrada", "Hora de Salida"]
if os.path.exists(archivo_ruta):
    df_asistencia = pd.read_excel(archivo_ruta, engine='openpyxl')
else:
    df_asistencia = pd.DataFrame(columns=columnas)

# 🔹 Formulario de registro de asistencia
st.title("Registro de Asistencia")
docente_seleccionado = st.selectbox("Seleccione un docente:", ["Seleccione un docente"] + [f"{d[1]} {d[2]} {d[3]}" for d in docentes])

hora_entrada = st.time_input("Hora de Entrada:", value=datetime.datetime.now().replace(second=0, microsecond=0).time())
hora_salida = st.time_input("Hora de Salida:", value=datetime.datetime.now().replace(second=0, microsecond=0).time())

if st.button("Registrar Asistencia"):
    if docente_seleccionado != "Seleccione un docente":
        if not df_asistencia[(df_asistencia["Nombre"] == docente_seleccionado) & (df_asistencia["Hora de Entrada"] == str(hora_entrada))].empty:
            st.warning("El docente ya ha sido registrado con esta hora de entrada.")
        else:
            nuevo_registro = pd.DataFrame([[docente_seleccionado, hora_entrada, hora_salida]], columns=columnas)
            df_asistencia = pd.concat([df_asistencia, nuevo_registro], ignore_index=True)
            df_asistencia.to_excel(archivo_ruta, index=False, engine='openpyxl')
            st.success("Asistencia registrada correctamente")
    else:
        st.warning("Debe seleccionar un docente.")

# 🔹 Mostrar la tabla de asistencia
st.subheader("Lista de Asistencia del día")
st.dataframe(df_asistencia)

# 🔹 Botón para generar archivo final y descargarlo
if st.button("Generar Lista de Asistencia para Firma"):
    df_asistencia.to_excel(archivo_ruta, index=False, engine='openpyxl')
    st.success(f"Lista de asistencia guardada en: {archivo_ruta}")
    st.balloons()  # 🎈 Efecto visual de confirmación

    # 🔹 Opción de descarga manual
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_asistencia.to_excel(writer, index=False, sheet_name="Asistencia")
    output.seek(0)
    st.download_button(label="Descargar Lista de Asistencia", data=output, file_name=nombre_archivo, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# 🔹 Confirmar sincronización con OneDrive
if os.path.exists(archivo_ruta):
    st.success("El archivo está en OneDrive y listo para imprimir.")
else:
    st.warning("No se pudo verificar la sincronización con OneDrive. Descargue el archivo manualmente.")

conn.close()
