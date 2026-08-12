import streamlit as st
from logic.iol_api import obtener_token, obtener_serie_historica


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
        serie = obtener_serie_historica(token, "AAPLD", "2021-01-01", "2026-08-08")

        st.subheader("Exploración temporal: serie histórica cruda de AAPLD")
        st.write(f"Cantidad de registros: {len(serie)}")
        st.json(serie[:3])
        st.json(serie[-3:])

    except Exception as e:
        st.error(f"Tipo de error: {type(e).__name__}")
        st.error(f"Detalle: {e}")
