import streamlit as st
from logic.iol_api import obtener_token, obtener_portafolio, obtener_operaciones
from logic.portafolio import portafolio_a_tabla
from logic.operaciones import operaciones_a_tabla, separar_lotes_y_caja, agregar_costo_en_ars
from logic.fifo import calcular_fifo, calcular_ppc_propio
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

        portafolio = obtener_portafolio(token)
        tabla_portafolio = portafolio_a_tabla(portafolio)

        operaciones = obtener_operaciones(token, "2023-01-01", "2026-08-08")
        tabla_operaciones = operaciones_a_tabla(operaciones)
        lotes, flujo_caja = separar_lotes_y_caja(tabla_operaciones)

        fechas_cortas = lotes["fechaOperada"].str[:10]
        tipos_cambio, fechas_fallidas = obtener_tipos_cambio_por_fecha(fechas_cortas)
        lotes_ars = agregar_costo_en_ars(lotes, tipos_cambio)

        posiciones_usd, realizado_usd = calcular_fifo(lotes, columna_precio="precio_ajustado")
        ppc_usd = calcular_ppc_propio(posiciones_usd)

        posiciones_ars, realizado_ars = calcular_fifo(lotes_ars, columna_precio="precio_ajustado_ars")
        ppc_ars = calcular_ppc_propio(posiciones_ars).rename(columns={
            "ppc_propio": "ppc_propio_ars",
            "costo_total": "costo_total_ars",
        })

        comparacion_ppc = ppc_usd.merge(
            ppc_ars[["simbolo", "ppc_propio_ars", "costo_total_ars"]],
            on="simbolo", how="left"
        ).merge(
            tabla_portafolio[["simbolo", "cantidad", "ppc_iol"]],
            on="simbolo", how="left"
        )

        st.success("Conexión con IOL exitosa ✅")

        st.subheader("PPC propio (USD y ARS) vs. PPC de IOL")
        st.dataframe(comparacion_ppc)

        if fechas_fallidas:
            st.warning(f"No se pudo obtener el tipo de cambio para estas fechas: {fechas_fallidas}")

    except Exception:
        st.error("No se pudo conectar con IOL. Revisá las credenciales configuradas.")
