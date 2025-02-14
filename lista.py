import streamlit as st
import pandas as pd
import datetime
import os
from io import BytesIO

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

# Directorio de almacenamiento en OneDrive
ONEDRIVE_PATH = r"C:\\Users\\sup11\\OneDrive\\Attachments\\Documentos\\Interfaces de phyton\\Lista de asistencia\\Listas de asistencia"
if not os.path.exists(ONEDRIVE_PATH):
    os.makedirs(ONEDRIVE_PATH)

# Registro de actividad y fecha
st.title("Registro de Actividad")
actividad = st.text_input("Ingrese el nombre de la actividad:")
fecha_actividad = st.date_input("Seleccione la fecha de la actividad:")

if not actividad or not fecha_actividad:
    st.warning("Debe ingresar la actividad y la fecha antes de continuar.")
    st.stop()

# Nombre del archivo de asistencia
nombre_archivo = f"Asistencia_{actividad}_{fecha_actividad}.xlsx"
archivo_ruta = os.path.join(ONEDRIVE_PATH, nombre_archivo)

# Inicializar dataframe de asistencia
columnas = ["Nombre", "Hora de Entrada", "Hora de Salida"]
if os.path.exists(archivo_ruta):
    df_asistencia = pd.read_excel(archivo_ruta, engine='openpyxl')
else:
    df_asistencia = pd.DataFrame(columns=columnas)

# Formulario de registro de asistencia
st.title("Registro de Asistencia")
nombre_docente = st.text_input("Nombre del Docente:")
hora_entrada = st.time_input("Hora de Entrada:", value=datetime.datetime.now().time())
hora_salida = st.time_input("Hora de Salida:", value=datetime.datetime.now().time())

if st.button("Registrar Asistencia"):
    if nombre_docente:
        nuevo_registro = pd.DataFrame([[nombre_docente, hora_entrada, hora_salida]], columns=columnas)
        df_asistencia = pd.concat([df_asistencia, nuevo_registro], ignore_index=True)
        df_asistencia.to_excel(archivo_ruta, index=False, engine='openpyxl')
        st.success("Asistencia registrada correctamente")
    else:
        st.warning("Debe ingresar el nombre del docente.")

# Mostrar la tabla de asistencia
st.subheader("Lista de Asistencia del día")
st.dataframe(df_asistencia)

# Botón para finalizar y generar archivo final
if st.button("Generar Lista de Asistencia para Firma"):
    df_asistencia.to_excel(archivo_ruta, index=False, engine='openpyxl')
    st.success(f"Lista de asistencia guardada en: {archivo_ruta}")
