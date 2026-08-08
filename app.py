import streamlit as st
from logic.iol_api import obtener_token, obtener_portafolio, obtener_operaciones
from logic.portafolio import portafolio_a_tabla
from logic.operaciones import operaciones_a_tabla, separar_lotes_y_caja
from logic.fifo import calcular_fifo


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
        tabla_portafolio = portafolio_a_tabla(portafolio)

        operaciones = obtener_operaciones(token, "2023-01-01", "2026-08-08")

        st.subheader("Exploración temporal: primera operación cruda")
        st.json(operaciones[0])

    except Exception as e:
        st.error(f"Tipo de error: {type(e).__name__}")
        st.error(f"Detalle: {e}")
