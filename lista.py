import streamlit as st
import pandas as pd
import datetime
import os
import sqlite3
from io import BytesIO
from docx import Document

# Configuración de la contraseña
PASSWORD = "defvm11"

# Estado de autenticación
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Página de inicio de sesión
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

# Directorios de almacenamiento en OneDrive
ONEDRIVE_PATH = r"C:\\Users\\sup11\\OneDrive\\Attachments\\Documentos\\Interfaces de phyton\\Lista de asistencia"
DB_PATH = os.path.join(ONEDRIVE_PATH, "asistencia.db")
DOCX_TEMPLATE_PATH = os.path.join(ONEDRIVE_PATH, "lista.docx")  # Plantilla Word
OUTPUT_DOCX_PATH = os.path.join(ONEDRIVE_PATH, "Listas de asistencia")

if not os.path.exists(OUTPUT_DOCX_PATH):
    os.makedirs(OUTPUT_DOCX_PATH)

# Verificar base de datos SQLite
def conectar_db():
    if not os.path.exists(DB_PATH):
        st.error(f"⚠️ La base de datos no existe en la ruta: {DB_PATH}")
        st.stop()
    try:
        conn = sqlite3.connect(DB_PATH)
        return conn
    except sqlite3.Error as e:
        st.error(f"⚠️ Error al conectar con la base de datos: {e}")
        st.stop()

# Obtener lista de docentes
def obtener_docentes():
    try:
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, apellido_paterno, apellido_materno, nombre FROM docentes WHERE activo = 1")
        docentes = cursor.fetchall()
        conn.close()
        return [f"{d[1]} {d[2]} {d[3]}" for d in docentes]
    except sqlite3.OperationalError:
        st.error("⚠️ Error al leer la tabla 'docentes'. Verifique la base de datos.")
        return []

# Registro de actividad y fecha
st.title("📌 Registro de Actividad")
actividad = st.text_input("Ingrese el nombre de la actividad:")
fecha_actividad = st.date_input("Seleccione la fecha de la actividad:")
if not actividad or not fecha_actividad:
    st.warning("⚠️ Debe ingresar la actividad y la fecha antes de continuar.")
    st.stop()

# Archivo de asistencia
nombre_archivo = f"Asistencia_{actividad}_{fecha_actividad}.xlsx"
archivo_ruta = os.path.join(ONEDRIVE_PATH, nombre_archivo)
columnas = ["No.", "Nombre Completo", "Hora de Entrada", "Firma Entrada", "Hora de Salida", "Firma Salida"]

# Verificar si el archivo Excel existe
if os.path.exists(archivo_ruta):
    try:
        df_asistencia = pd.read_excel(archivo_ruta, engine='openpyxl')
    except Exception as e:
        st.error(f"⚠️ Error al leer el archivo de asistencia: {e}")
        df_asistencia = pd.DataFrame(columns=columnas)
else:
    df_asistencia = pd.DataFrame(columns=columnas)

# Formulario de registro de asistencia
st.title("📋 Registro de Asistencia")
docentes = obtener_docentes()
nombres_docentes = st.multiselect("Seleccione los Docentes:", docentes)
hora_entrada = st.time_input("Hora de Entrada:")
hora_salida = st.time_input("Hora de Salida:")

if st.button("Registrar Asistencia"):
    if nombres_docentes:
        for i, nombre_docente in enumerate(nombres_docentes):
            hora_entrada_adjusted = (datetime.datetime.combine(datetime.date.today(), hora_entrada) + datetime.timedelta(minutes=i)).time()
            nuevo_registro = pd.DataFrame([[len(df_asistencia)+1, nombre_docente, str(hora_entrada_adjusted), "", str(hora_salida), ""]], columns=columnas)
            df_asistencia = pd.concat([df_asistencia, nuevo_registro], ignore_index=True)
        df_asistencia.to_excel(archivo_ruta, index=False, engine='openpyxl')
        st.success("✅ Asistencia registrada correctamente")
    else:
        st.warning("⚠️ Debe seleccionar al menos un docente.")

# Generar documento en Word respetando la plantilla
def generar_docx():
    if not os.path.exists(DOCX_TEMPLATE_PATH):
        st.error("⚠️ La plantilla de Word no existe.")
        return None
    
    doc = Document(DOCX_TEMPLATE_PATH)
    
    # Reemplazar marcadores en el documento
    for p in doc.paragraphs:
        if "{{actividad}}" in p.text:
            p.text = p.text.replace("{{actividad}}", actividad)
        if "{{fecha}}" in p.text:
            p.text = p.text.replace("{{fecha}}", str(fecha_actividad))

    # Agregar tabla de asistencia
    tabla = doc.add_table(rows=1, cols=len(columnas))
    for i, columna in enumerate(columnas):
        tabla.cell(0, i).text = columna
    for _, row in df_asistencia.iterrows():
        fila = tabla.add_row().cells
        for i, valor in enumerate(row):
            fila[i].text = str(valor)

    # Guardar el archivo generado
    output_doc_path = os.path.join(OUTPUT_DOCX_PATH, f"Asistencia_{actividad}_{fecha_actividad}.docx")
    doc.save(output_doc_path)
    return output_doc_path

# Botón para generar documento Word
if st.button("📄 Generar Lista de Asistencia para Firma"):
    df_asistencia.to_excel(archivo_ruta, index=False, engine='openpyxl')
    docx_path = generar_docx()
    if docx_path:
        with open(docx_path, "rb") as f:
            st.download_button("⬇️ Descargar Lista de Asistencia en Word", f, file_name=os.path.basename(docx_path), mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
