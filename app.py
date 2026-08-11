import streamlit as st
from logic.iol_api import obtener_token
from logic.dolar import obtener_tipo_cambio


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
        tipo_cambio = obtener_tipo_cambio("2026-07-13")

        st.subheader("Exploración temporal: tipo de cambio crudo")
        st.json(tipo_cambio)

    except Exception as e:
        st.error(f"Tipo de error: {type(e).__name__}")
        st.error(f"Detalle: {e}")
