@echo off
cd /d "C:\Users\sup11\OneDrive\Attachments\Documentos\Interfaces de phyton\Lista de asistencia"
python -m pip install --user streamlit
start "" python -m streamlit run lista.py
exit
