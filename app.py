import streamlit as st
from logic.iol_api import obtener_token, obtener_portafolio

def mostrar_login():
    st.title("Iniciar sesión")
    usuario = st.text_input("Usuario")
    contraseña = st.text_input("Contraseña", type="password")
    if st.button("Ingresar"):
        if usuario == st.secrets["APP_USER"] and contraseña == st.secrets["APP_PASSWORD"]:
            st.session_state["autenticado"] = True
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos")

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    mostrar_login()
else:
    st.title("Mi Dashboard de Inversiones")
    try:
        token = obtener_token()
        portafolio = obtener_portafolio(token)
        st.success("Conexión con IOL exitosa ✅")
        st.json(portafolio)
    except Exception:
        st.error("No se pudo conectar con IOL. Revisá las credenciales configuradas.")
