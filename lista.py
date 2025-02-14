import streamlit as st
import pandas as pd
import datetime
import os
from io import BytesIO
from PIL import Image
import base64

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
ONEDRIVE_PATH = "C:\\Users\\sup11\\OneDrive\\Attachments\\Documentos\\Interfaces de phyton\\Lista de asistencia\\Listas de asistencia"
if not os.path.exists(ONEDRIVE_PATH):
    os.makedirs(ONEDRIVE_PATH)

# Registro de actividad y fecha
st.title("Registro de Actividad")
actividad = st.text_input("Ingrese el nombre de la actividad:")
fecha_actividad = st.date_input("Seleccione la fecha de la actividad:")

if not actividad or not fecha_actividad:
    st.warning("Debe ingresar la actividad y la fecha antes de continuar.")
    st.stop()

# Cargar base de datos de docentes desde la plantilla en OneDrive
PLANTILLA_PATH = "C:\Users\sup11\OneDrive\Attachments\Documentos\Interfaces de phyton\Lista de asistencia\PLANTILLA.xlsx"
