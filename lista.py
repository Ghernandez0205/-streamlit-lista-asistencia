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

# Conectar con SQLite y verificar la existencia de la base de datos
def conectar_db():
    if not os.path.exists(DB_PATH):
        st.error(f"La base de datos no existe en la ruta: {DB_PATH}")
        st.stop()
    try:
        conn = sqlite3.connect(DB_PATH)
        return conn
    except sqlite3.Error as e:
        st.error(f"Error al conectar con la base de datos: {e}")
        st.stop()

# Verificar y crear la tabla docentes si no existe
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

# Obtener lista de docentes
def obtener_docentes():
    verificar_tabla()
    try:
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, apellido_paterno, apellido_materno, nombre FROM docentes WHERE activo = 1")
        docentes = cursor.fetchall()
        conn.close()
        return [f"{d[1]} {d[2]} {d[3]}" for d in docentes]
    except sqlite3.OperationalError:
        st.error("Error al leer la tabla 'docentes'. Verifique que la base de datos esté correctamente configurada.")
        return []

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

# Verificar si el archivo Excel existe
if os.path.exists(archivo_ruta):
    try:
        df_asistencia = pd.read_excel(archivo_ruta, engine='openpyxl')
    except Exception as e:
        st.error(f"Error al leer el archivo de asistencia: {e}")
        df_asistencia = pd.DataFrame(columns=columnas)
else:
    df_asistencia = pd.DataFrame(columns=columnas)

# Formulario de registro de asistencia
st.title("Registro de Asistencia")
docentes = obtener_docentes()
docentes_seleccionados = st.multiselect("Seleccione los Docentes:", docentes)
hora_entrada = st.time_input("Hora de Entrada:")
hora_salida = st.time_input("Hora de Salida:")

if st.button("Registrar Asistencia"):
    if docentes_seleccionados:
        nuevos_registros = []
        for nombre_docente in docentes_seleccionados:
            nuevos_registros.append([len(df_asistencia) + 1, nombre_docente, str(hora_entrada), "", str(hora_salida), ""])
        
        # Convertir lista en DataFrame y concatenar
        df_nuevos = pd.DataFrame(nuevos_registros, columns=columnas)
        df_asistencia = pd.concat([df_asistencia, df_nuevos], ignore_index=True)

        # Guardar en Excel
        df_asistencia.to_excel(archivo_ruta, index=False, engine='openpyxl')
        st.success("Asistencia registrada correctamente")
    else:
        st.warning("Debe seleccionar al menos un docente.")

# Mostrar tabla de asistencia solo si hay registros
st.subheader("Lista de Asistencia del día")
if not df_asistencia.empty:
    st.dataframe(df_asistencia)
else:
    st.warning("No hay registros de asistencia disponibles.")

# Generar documento en Word
def generar_docx():
    doc = Document()
    doc.add_paragraph("Servicios Educativos Integrados Al Estado de México\nSupervisión 11 de Educación Física Valle de México")
    doc.add_paragraph(f"Lista de asistencia: {actividad}")
    doc.add_paragraph(f"Fecha: {fecha_actividad}")
    tabla = doc.add_table(rows=1, cols=len(columnas))
    
    # Agregar encabezados
    for i, columna in enumerate(columnas):
        tabla.cell(0, i).text = columna

    # Agregar registros
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
