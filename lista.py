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

# 📂 Definir rutas de almacenamiento
ONEDRIVE_PATH = os.path.expanduser("~/OneDrive/Attachments/Documentos/Interfaces de phyton/Lista de asistencia")
DB_PATH = os.path.join(ONEDRIVE_PATH, "asistencia.db")
DOCX_PATH = os.path.join(ONEDRIVE_PATH, "lista.docx")

# Asegurar que la carpeta de almacenamiento existe
if not os.path.exists(ONEDRIVE_PATH):
    os.makedirs(ONEDRIVE_PATH)

# 📌 **Conectar con SQLite y verificar la existencia de la base de datos**
def conectar_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        return conn
    except sqlite3.Error as e:
        st.error(f"Error al conectar con la base de datos: {e}")
        st.stop()

# 📌 **Crear tabla si no existe**
def verificar_tabla():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS docentes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            apellido_paterno TEXT NOT NULL,
            apellido_materno TEXT NOT NULL,
            nombre TEXT NOT NULL,
            activo INTEGER DEFAULT 1
        )
    ''')
    conn.commit()
    conn.close()

# 📌 **Obtener la lista de docentes**
def obtener_docentes():
    verificar_tabla()
    try:
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, apellido_paterno, apellido_materno, nombre FROM docentes WHERE activo = 1")
        docentes = cursor.fetchall()
        conn.close()
        return [f"{d[1]} {d[2]} {d[3]}" for d in docentes]
    except sqlite3.OperationalError as e:
        st.error(f"Error al leer la tabla 'docentes': {e}")
        return []

# 📌 **Registro de actividad**
st.title("Registro de Actividad")
actividad = st.text_input("Ingrese el nombre de la actividad:")
fecha_actividad = st.date_input("Seleccione la fecha de la actividad:")

if not actividad or not fecha_actividad:
    st.warning("Debe ingresar la actividad y la fecha antes de continuar.")
    st.stop()

# 📂 **Manejo del archivo de asistencia**
nombre_archivo = f"Asistencia_{actividad}_{fecha_actividad}.xlsx"
archivo_ruta = os.path.join(ONEDRIVE_PATH, nombre_archivo)
columnas = ["No.", "Nombre Completo", "Hora de Entrada", "Firma", "Hora de Salida", "Firma"]

# 📂 **Cargar el archivo de asistencia**
if os.path.exists(archivo_ruta):
    try:
        df_asistencia = pd.read_excel(archivo_ruta, engine='openpyxl')
    except Exception as e:
        st.error(f"Error al leer el archivo de asistencia: {e}")
        df_asistencia = pd.DataFrame(columns=columnas)
else:
    df_asistencia = pd.DataFrame(columns=columnas)

# 📌 **Formulario de Registro**
st.title("Registro de Asistencia")
docentes = obtener_docentes()
nombre_docente = st.selectbox("Seleccione el Docente:", ["Seleccionar..."] + docentes)
hora_entrada = st.time_input("Hora de Entrada:")
hora_salida = st.time_input("Hora de Salida:")

if st.button("Registrar Asistencia"):
    if nombre_docente != "Seleccionar...":
        nuevo_registro = pd.DataFrame([[len(df_asistencia)+1, nombre_docente, str(hora_entrada), "", str(hora_salida), ""]], columns=columnas)
        df_asistencia = pd.concat([df_asistencia, nuevo_registro], ignore_index=True)
        df_asistencia.to_excel(archivo_ruta, index=False, engine='openpyxl')
        st.success("Asistencia registrada correctamente")
    else:
        st.warning("Debe seleccionar un docente.")

# 📌 **Mostrar la tabla de asistencia**
st.subheader("Lista de Asistencia del día")
if not df_asistencia.empty:
    st.dataframe(df_asistencia)
else:
    st.warning("No hay registros de asistencia disponibles.")

# 📌 **Generar documento en Word**
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

# 📌 **Botón para generar documento en Word**
if st.button("Generar Lista de Asistencia para Firma"):
    df_asistencia.to_excel(archivo_ruta, index=False, engine='openpyxl')
    st.success(f"Lista de asistencia guardada en: {archivo_ruta}")
    docx_path = generar_docx()
    with open(docx_path, "rb") as f:
        st.download_button("Descargar Lista de Asistencia en Word", f, file_name="Lista_Asistencia.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
