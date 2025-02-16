import streamlit as st
import pandas as pd
import datetime
import sqlite3
import os
from io import BytesIO

# Configuración de autenticación
PASSWORD = "defvm11"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

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

# Ruta de la base de datos SQLite
db_path = r"C:\Users\sup11\OneDrive\Attachments\Documentos\Interfaces de phyton\Lista de asistencia\asistencia.db"

# Ruta de almacenamiento en OneDrive
ONEDRIVE_PATH = r"C:\Users\sup11\OneDrive\Attachments\Documentos\Interfaces de phyton\Lista de asistencia\Listas de asistencia"
if not os.path.exists(ONEDRIVE_PATH):
    os.makedirs(ONEDRIVE_PATH)

# Función para obtener docentes activos
def obtener_docentes():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, apellido_paterno, apellido_materno, nombre FROM docentes WHERE activo = 1")
    docentes = cursor.fetchall()
    conn.close()
    return [f"{d[1]} {d[2]} {d[3]}" for d in docentes]  # Formato: Apellido Paterno Apellido Materno Nombre

# Registro de actividad
st.title("Registro de Actividad")
actividad = st.text_input("Ingrese el nombre de la actividad:")
fecha_actividad = st.date_input("Seleccione la fecha de la actividad:")

if not actividad or not fecha_actividad:
    st.warning("Debe ingresar la actividad y la fecha antes de continuar.")
    st.stop()

# Nombre del archivo de asistencia
nombre_archivo = f"Asistencia_{actividad}_{fecha_actividad}.xlsx"
archivo_ruta = os.path.join(ONEDRIVE_PATH, nombre_archivo)

# Obtener lista de docentes desde la base de datos
docentes = obtener_docentes()

# Inicializar DataFrame de asistencia
columnas = ["Nombre", "Hora de Entrada", "Hora de Salida"]
if os.path.exists(archivo_ruta):
    df_asistencia = pd.read_excel(archivo_ruta, engine='openpyxl')
else:
    df_asistencia = pd.DataFrame(columns=columnas)

# Formulario de registro de asistencia
st.title("Registro de Asistencia")
docente_seleccionado = st.selectbox("Seleccione un docente:", docentes)
hora_entrada = st.time_input("Hora de Entrada:", value=datetime.datetime.now().replace(second=0, microsecond=0).time())
hora_salida = st.time_input("Hora de Salida:", value=datetime.datetime.now().replace(second=0, microsecond=0).time())

if st.button("Registrar Asistencia"):
    if docente_seleccionado:
        if not df_asistencia[(df_asistencia["Nombre"] == docente_seleccionado) & (df_asistencia["Hora de Entrada"] == str(hora_entrada))].empty:
            st.warning("El docente ya ha sido registrado con esta hora de entrada.")
        else:
            nuevo_registro = pd.DataFrame([[docente_seleccionado, hora_entrada, hora_salida]], columns=columnas)
            df_asistencia = pd.concat([df_asistencia, nuevo_registro], ignore_index=True)
            df_asistencia.to_excel(archivo_ruta, index=False, engine='openpyxl')
            st.success("Asistencia registrada correctamente")
    else:
        st.warning("Debe seleccionar un docente.")

# Mostrar la tabla de asistencia
st.subheader("Lista de Asistencia del día")
st.dataframe(df_asistencia)

# Botón para finalizar y generar archivo final
if st.button("Generar Lista de Asistencia para Firma"):
    df_asistencia.to_excel(archivo_ruta, index=False, engine='openpyxl')
    st.success(f"Lista de asistencia guardada en: {archivo_ruta}")
    st.balloons()
    
    # Opción de descarga manual
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_asistencia.to_excel(writer, index=False, sheet_name="Asistencia")
    output.seek(0)
    st.download_button(label="Descargar Lista de Asistencia", data=output, file_name=nombre_archivo, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# Confirmar sincronización con OneDrive
if os.path.exists(archivo_ruta):
    st.success("El archivo está en OneDrive y listo para imprimir.")
else:
    st.warning("No se pudo verificar la sincronización con OneDrive. Descargue el archivo manualmente.")

