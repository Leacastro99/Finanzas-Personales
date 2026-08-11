import streamlit as st
from logic.iol_api import obtener_token, obtener_operaciones
from logic.operaciones import operaciones_a_tabla, separar_lotes_y_caja, agregar_costo_en_ars
from logic.dolar import obtener_tipos_cambio_por_fecha


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

        operaciones = obtener_operaciones(token, "2023-01-01", "2026-08-08")
        tabla_operaciones = operaciones_a_tabla(operaciones)
        lotes, flujo_caja = separar_lotes_y_caja(tabla_operaciones)

        fechas_cortas = lotes["fechaOperada"].str[:10]
        tipos_cambio = obtener_tipos_cambio_por_fecha(fechas_cortas)
        lotes_con_ars = agregar_costo_en_ars(lotes, tipos_cambio)

        st.subheader("Exploración: lotes con tipo de cambio y costo en ARS")
        st.dataframe(lotes_con_ars[["simbolo", "tipo", "fecha_corta", "precio_ajustado", "tipo_cambio", "precio_ajustado_ars"]])

    except Exception as e:
        st.error(f"Tipo de error: {type(e).__name__}")
        st.error(f"Detalle: {e}")
