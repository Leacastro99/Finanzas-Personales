import streamlit as st
from logic.iol_api import obtener_token

st.title("Mi Dashboard de Inversiones")

try:
    token = obtener_token()
    st.success("Conexión con IOL exitosa ✅")
except Exception as e:
    st.error(f"Error al conectar con IOL: {e}")
