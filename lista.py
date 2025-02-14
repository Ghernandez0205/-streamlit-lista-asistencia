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
    st.title("Sistema de Registro de Asistencia")
    password_input = st.text_input("Ingrese la contraseña:", type="password")
    if st.button("Ingresar"):
        if password_input == PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Contraseña incorrecta")
    st.stop()

# Directorio de almacenamiento en Streamlit Cloud
ONEDRIVE_PATH = "./Listas_de_asistencia/"
if not os.path.exists(ONEDRIVE_PATH):
    os.makedirs(ONEDRIVE_PATH)

# Registro de actividad y fecha
st.title("Registro de Actividad")
actividad = st.text_input("Ingrese el nombre de la actividad:")
fecha_actividad = st.date_input("Seleccione la fecha de la actividad:")

if not actividad or not fecha_actividad:
    st.warning("Debe ingresar la actividad y la fecha antes de continuar.")
    st.stop()

# Cargar base de datos de docentes desde el repositorio
PLANTILLA_PATH = "PLANTILLA 29D AUDITORIA.xlsx"
docentes_df = pd.read_excel(PLANTILLA_PATH, engine='openpyxl')
docentes = docentes_df[['APELLIDO PATERNO', 'APELLIDO MATERNO', 'NOMBRE (S)']].astype(str).apply(lambda x: ' '.join(x.dropna()), axis=1).tolist()

# Formulario de registro de asistencia
st.title("Registro de Asistencia")
nombres_seleccionados = st.multiselect("Seleccione los nombres:", docentes)
hora_entrada = st.time_input("Hora de Entrada", value=datetime.datetime.now().replace(second=0, microsecond=0).time())
hora_salida = st.time_input("Hora de Salida", value=datetime.datetime.now().replace(second=0, microsecond=0).time())

# Guardar datos en archivo con formato específico
if st.button("Registrar Asistencia"):
    fecha = fecha_actividad.strftime("%Y%m%d")
    folio = len(os.listdir(ONEDRIVE_PATH)) + 1
    archivo_nombre = f"asistencia_{actividad}_{fecha}_{folio}.xlsx"
    archivo_ruta = os.path.join(ONEDRIVE_PATH, archivo_nombre)
    
    # Cargar o crear el archivo de asistencia
    if os.path.exists(archivo_ruta):
        df = pd.read_excel(archivo_ruta, engine='openpyxl')
    else:
        df = pd.DataFrame(columns=["Fecha", "Actividad", "Nombre", "Hora de Entrada", "Hora de Salida"])
    
    # Agregar nuevo registro
    nuevo_registro = pd.DataFrame({
        "Fecha": [fecha_actividad] * len(nombres_seleccionados),
        "Actividad": [actividad] * len(nombres_seleccionados),
        "Nombre": nombres_seleccionados,
        "Hora de Entrada": [hora_entrada] * len(nombres_seleccionados),
        "Hora de Salida": [hora_salida] * len(nombres_seleccionados)
    })
    df = pd.concat([df, nuevo_registro], ignore_index=True)
    df.to_excel(archivo_ruta, index=False, engine='openpyxl')
    st.success(f"Registro guardado correctamente en {archivo_nombre}")

# Mostrar la tabla de asistencia
st.subheader("Lista de Asistencia del día")
if os.path.exists(archivo_ruta):
    df = pd.read_excel(archivo_ruta, engine='openpyxl')
    st.dataframe(df)

# Confirmación para generar lista final con autenticación
if st.button("Generar Lista de Asistencia"):
    confirm_password = st.text_input("Ingrese la contraseña nuevamente para confirmar:", type="password")
    if confirm_password == PASSWORD:
        st.success("Lista de asistencia generada con éxito. Puede descargar el archivo.")
    else:
        st.error("Contraseña incorrecta. No se puede generar la lista.")
    
# Botón para descargar el archivo Excel
def get_table_download_link(df):
    """Genera un archivo descargable de Excel"""
    from io import BytesIO
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return output

if os.path.exists(archivo_ruta):
    st.download_button(
        label="Descargar Asistencia",
        data=get_table_download_link(df),
        file_name=archivo_nombre,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
