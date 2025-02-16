import streamlit as st
import sqlite3
import os

# 🔹 Permitir subir la base de datos manualmente
st.title("Cargar Base de Datos SQLite")
archivo_subido = st.file_uploader("Sube el archivo 'asistencia.db'", type=["db"])

if archivo_subido is not None:
    DB_PATH = "asistencia.db"
    with open(DB_PATH, "wb") as f:
        f.write(archivo_subido.getbuffer())

    st.success("Base de datos cargada correctamente.")

# 🔹 Conectar a la base de datos si ya existe
if os.path.exists("asistencia.db"):
    conn = sqlite3.connect("asistencia.db")
    cursor = conn.cursor()
    st.success("Conexión establecida con la base de datos.")
else:
    st.error("No se encontró la base de datos. Por favor, sube un archivo válido.")
