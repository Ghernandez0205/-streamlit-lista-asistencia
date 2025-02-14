import streamlit as st
import pandas as pd
import datetime
import os

# Configuración de la contraseña
PASSWORD = "defvm11"

# Estado de autenticación
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Página de inicio de sesión
if not st.session_state.authenticated:
    st.title("Acceso al Registro de Asistencia")
    password_input = st.text_input("Ingrese la contraseña:", type="password")
    if st.button("Ingresar"):
        if password_input == PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Contraseña incorrecta")
    st.stop()

# Registro de actividad antes de asistencia
if "actividad_registrada" not in st.session_state:
    st.session_state.actividad_registrada = False

if not st.session_state.actividad_registrada:
    st.title("Registro de Actividad")
    actividad = st.text_input("Ingrese la actividad:")
    fecha_actividad = st.date_input("Seleccione la fecha de la actividad", datetime.date.today())

    if st.button("Registrar Actividad"):
        st.session_state.actividad = actividad
        st.session_state.fecha_actividad = fecha_actividad.strftime("%Y-%m-%d")
        st.session_state.actividad_registrada = True
        st.success("Actividad registrada correctamente.")
        st.rerun()
    st.stop()

# Directorio de almacenamiento en Streamlit Cloud
ONEDRIVE_PATH = "./Listas_de_asistencia/"
if not os.path.exists(ONEDRIVE_PATH):
    os.makedirs(ONEDRIVE_PATH)

# Cargar base de datos de docentes
PLANTILLA_PATH = "PLANTILLA 29D AUDITORIA.xlsx"
docentes_df = pd.read_excel(PLANTILLA_PATH, engine='openpyxl')
docentes = docentes_df[['APELLIDO PATERNO', 'APELLIDO MATERNO', 'NOMBRE (S)']].astype(str).apply(lambda x: ' '.join(x.dropna()), axis=1).tolist()

# Formulario de registro de asistencia
st.title("Registro de Asistencia")
st.write(f"**Actividad:** {st.session_state.actividad}")
st.write(f"**Fecha:** {st.session_state.fecha_actividad}")

nombres_seleccionados = st.multiselect("Seleccione los docentes:", docentes)
hora_entrada = st.time_input("Hora de Entrada", value=datetime.datetime.now().replace(second=0, microsecond=0).time())
hora_salida = st.time_input("Hora de Salida", value=datetime.datetime.now().replace(second=0, microsecond=0).time())

# Guardar datos en archivo con formato específico
if st.button("Registrar Asistencia"):
    fecha = st.session_state.fecha_actividad.replace("-", "")
    archivo_nombre = f"asistencia_{fecha}.xlsx"
    archivo_ruta = os.path.join(ONEDRIVE_PATH, archivo_nombre)

    # Cargar o crear el archivo de asistencia
    if os.path.exists(archivo_ruta):
        df = pd.read_excel(archivo_ruta, engine='openpyxl')
    else:
        df = pd.DataFrame(columns=["Fecha", "Nombre", "Hora de Entrada", "Hora de Salida"])

    # Agregar nuevo registro
    nuevo_registro = pd.DataFrame({
        "Fecha": [st.session_state.fecha_actividad] * len(nombres_seleccionados),
        "Nombre": nombres_seleccionados,
        "Hora de Entrada": [hora_entrada.strftime("%H:%M")] * len(nombres_seleccionados),
        "Hora de Salida": [hora_salida.strftime("%H:%M")] * len(nombres_seleccionados)
    })
    
    df = pd.concat([df, nuevo_registro], ignore_index=True)
    df.to_excel(archivo_ruta, index=False, engine='openpyxl')
    st.success(f"Registro guardado correctamente.")

# Mostrar la tabla de asistencia
st.subheader("Lista de Asistencia del día")
if os.path.exists(archivo_ruta):
    df = pd.read_excel(archivo_ruta, engine='openpyxl')
    st.dataframe(df)

# Confirmación para generar lista de asistencia
if st.button("Generar Lista de Asistencia para Firma"):
    confirm_password = st.text_input("Ingrese la contraseña para confirmar:", type="password")
    if confirm_password == PASSWORD:
        st.success("Lista de asistencia generada con éxito. Puede descargarla a continuación.")
        st.download_button(
            label="Descargar Lista de Asistencia",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name=archivo_nombre.replace(".xlsx", ".csv"),
            mime="text/csv"
        )
    else:
        st.error("Contraseña incorrecta.")

# Botón para cerrar sesión
if st.button("Cerrar sesión"):
    st.session_state.authenticated = False
    st.session_state.actividad_registrada = False
    st.rerun()
