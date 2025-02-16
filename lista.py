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

# Directorios de almacenamiento
ONEDRIVE_PATH = r"C:\\Users\\sup11\\OneDrive\\Attachments\\Documentos\\Interfaces de phyton\\Lista de asistencia"
DB_PATH = os.path.join(ONEDRIVE_PATH, "asistencia.db")
DOCX_PATH = os.path.join(ONEDRIVE_PATH, "lista.docx")
if not os.path.exists(ONEDRIVE_PATH):
    os.makedirs(ONEDRIVE_PATH)

# Conectar con SQLite
def conectar_db():
    conn = sqlite3.connect(DB_PATH)
    return conn

# Obtener lista de docentes
def obtener_docentes():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, apellido_paterno, apellido_materno, nombre FROM docentes WHERE activo = 1")
    docentes = cursor.fetchall()
    conn.close()
    return [f"{d[1]} {d[2]} {d[3]}" for d in docentes]

# Registro de actividad y fecha
st.title("Registro de Actividad")
actividad = st.text_input("Ingrese el nombre de la actividad:")
fecha_actividad = st.date_input("Seleccione la fecha de la actividad:")
if not actividad or not fecha_actividad:
    st.warning("Debe ingresar la actividad y la fecha antes de continuar.")
    st.stop()

# Archivo de asistencia
nombre_archivo = f"Asistencia_{actividad}_{fecha_actividad}.xlsx"
archivo_ruta = os.path.join(ONEDRIVE_PATH, nombre_archivo)
columnas = ["No.", "Nombre Completo", "Hora de Entrada", "Firma", "Hora de Salida", "Firma"]

if os.path.exists(archivo_ruta):
    df_asistencia = pd.read_excel(archivo_ruta, engine='openpyxl')
else:
    df_asistencia = pd.DataFrame(columns=columnas)

# Formulario de registro de asistencia
st.title("Registro de Asistencia")
docentes = obtener_docentes()
nombre_docente = st.selectbox("Seleccione el Docente:", ["Seleccionar..."] + docentes)
hora_entrada = st.time_input("Hora de Entrada:")
hora_salida = st.time_input("Hora de Salida:")

if st.button("Registrar Asistencia"):
    if nombre_docente != "Seleccionar...":
        nuevo_registro = pd.DataFrame([[len(df_asistencia)+1, nombre_docente, hora_entrada, "", hora_salida, ""]], columns=columnas)
        df_asistencia = pd.concat([df_asistencia, nuevo_registro], ignore_index=True)
        df_asistencia.to_excel(archivo_ruta, index=False, engine='openpyxl')
        st.success("Asistencia registrada correctamente")
    else:
        st.warning("Debe seleccionar un docente.")

# Mostrar tabla de asistencia
st.subheader("Lista de Asistencia del día")
st.dataframe(df_asistencia)

# Generar documento en Word
def generar_docx():
    doc = Document()
    doc.add_paragraph("Servicios Educativos Integrados Al Estado de México\nSupervisión 11 de Educación Física Valle de México")
    doc.add_paragraph(f"Lista de asistencia: {actividad}")
    doc.add_paragraph(f"Fecha: {fecha_actividad}")
    tabla = doc.add_table(rows=1, cols=len(columnas))
    for i, columna in enumerate(columnas):
        tabla.cell(0, i).text = columna
    for index, row in df_asistencia.iterrows():
        fila = tabla.add_row().cells
        for i, valor in enumerate(row):
            fila[i].text = str(valor)
    doc.add_paragraph("\nATENTAMENTE\nDOCTOR\nGUZMAN HERNANDEZ ESTRADA\nINSPECTOR DE LA SUPERVISIÓN 11")
    doc.save(DOCX_PATH)
    return DOCX_PATH

# Botón para generar documento Word
if st.button("Generar Lista de Asistencia para Firma"):
    df_asistencia.to_excel(archivo_ruta, index=False, engine='openpyxl')
    st.success(f"Lista de asistencia guardada en: {archivo_ruta}")
    docx_path = generar_docx()
    with open(docx_path, "rb") as f:
        st.download_button("Descargar Lista de Asistencia en Word", f, file_name="Lista_Asistencia.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
