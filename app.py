import streamlit as st
from datetime import date
from logic.iol_api import (
    obtener_token, obtener_portafolio, obtener_operaciones,
    obtener_cotizaciones_actuales, obtener_series_todas_posiciones
)
from logic.portafolio import portafolio_a_tabla
from logic.operaciones import (
    operaciones_a_tabla, separar_lotes_y_caja, SIMBOLO_A_SUFIJO_D, agregar_costo_en_ars
)
from logic.fifo import (
    calcular_fifo, calcular_ppc_propio, calcular_resultado_no_realizado,
    calcular_kpis, formatear_moneda
)
from logic.dividendos import resumen_flujo_caja, resultado_neto_por_simbolo
from logic.dolar import obtener_tipos_cambio_por_fecha, obtener_tipo_cambio_mas_cercano
from logic.evolucion import series_a_tabla, evolucion_valor_cartera


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

        # --- Tenencia actual (según IOL) ---
        portafolio = obtener_portafolio(token)
        tabla_portafolio = portafolio_a_tabla(portafolio)

        # --- Operaciones históricas: lotes y flujo de caja ---
        operaciones = obtener_operaciones(token, "2023-01-01", "2026-08-08")
        tabla_operaciones = operaciones_a_tabla(operaciones)
        lotes, flujo_caja = separar_lotes_y_caja(tabla_operaciones)

        # --- FIFO en USD ---
        posiciones, realizado = calcular_fifo(lotes, columna_precio="precio_ajustado")
        ppc_usd = calcular_ppc_propio(posiciones)

        # --- FIFO en ARS (con tipo de cambio histórico) ---
        fechas_cortas = lotes["fechaOperada"].str[:10]
        tipos_cambio, fechas_fallidas = obtener_tipos_cambio_por_fecha(fechas_cortas)
        lotes_ars = agregar_costo_en_ars(lotes, tipos_cambio)
        posiciones_ars, _ = calcular_fifo(lotes_ars, columna_precio="precio_ajustado_ars")
        ppc_ars = calcular_ppc_propio(posiciones_ars).rename(columns={
            "ppc_propio": "ppc_propio_ars", "costo_total": "costo_total_ars"
        })

        comparacion_ppc = ppc_usd.merge(
            ppc_ars[["simbolo", "ppc_propio_ars", "costo_total_ars"]], on="simbolo", how="left"
        ).merge(
            tabla_portafolio[["simbolo", "cantidad", "ppc_iol"]], on="simbolo", how="left"
        )

        # --- Flujo de caja: dividendos, renta, amortización ---
        tabla_flujo_caja = resumen_flujo_caja(flujo_caja)
        tabla_resultado_neto = resultado_neto_por_simbolo(realizado, tabla_flujo_caja)

        # --- Resultado no realizado (tenencia abierta) ---
        precios_actuales = obtener_cotizaciones_actuales(token, list(posiciones.keys()), SIMBOLO_A_SUFIJO_D)
        tabla_no_realizado = calcular_resultado_no_realizado(posiciones, precios_actuales)

        # --- Evolución del valor de la cartera (último año, simplificado) ---
        cantidades_actuales = {s: sum(l["cantidad"] for l in lts) for s, lts in posiciones.items()}
        series_crudas = obtener_series_todas_posiciones(
            token, list(posiciones.keys()), SIMBOLO_A_SUFIJO_D, "2025-08-08", "2026-08-08"
        )
        tabla_series = series_a_tabla(series_crudas)
        evolucion = evolucion_valor_cartera(tabla_series, cantidades_actuales)

        # --- KPIs ---
        kpis = calcular_kpis(tabla_portafolio, tabla_no_realizado, tabla_resultado_neto, posiciones, precios_actuales)

        st.success("Conexión con IOL exitosa ✅")

        moneda_elegida = st.radio("Moneda", ["USD", "ARS"], horizontal=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            if moneda_elegida == "USD":
                st.metric("Valor total", formatear_moneda(kpis["valor_total_usd"]))
            else:
                st.metric("Valor total", formatear_moneda(kpis["valor_total_ars"], "$"))
        with col2:
            st.metric("No realizado (USD)", formatear_moneda(kpis["resultado_no_realizado_usd"]))
        with col3:
            st.metric("Realizado + renta (USD)", formatear_moneda(kpis["resultado_neto_usd"]))

        st.subheader("Evolución del valor de la cartera (último año, simplificado)")
        st.line_chart(evolucion.set_index("fecha")["valor"])

        st.subheader("Resultado NO realizado (tenencia abierta)")
        st.dataframe(
            tabla_no_realizado,
            column_config={
                "ppc_propio": st.column_config.NumberColumn("PPC propio (USD)", format="%.2f"),
                "precio_actual": st.column_config.NumberColumn("Precio actual (USD)", format="%.2f"),
                "resultado_no_realizado": st.column_config.NumberColumn("Result. no realizado (USD)", format="%.2f"),
            }
        )

        st.subheader("Resultado neto por símbolo (capital + renta/dividendos)")
        st.dataframe(
            tabla_resultado_neto,
            column_config={
                "resultado_capital": st.column_config.NumberColumn("Resultado capital (USD)", format="%.2f"),
                "flujo_caja_cobrado": st.column_config.NumberColumn("Flujo de caja (USD)", format="%.2f"),
                "resultado_neto": st.column_config.NumberColumn("Resultado neto (USD)", format="%.2f"),
            }
        )

        st.subheader("PPC propio (USD y ARS) vs. PPC de IOL")
        st.dataframe(
            comparacion_ppc,
            column_config={
                "ppc_propio": st.column_config.NumberColumn("PPC propio (USD)", format="%.2f"),
                "costo_total": st.column_config.NumberColumn("Costo total (USD)", format="%.2f"),
                "ppc_propio_ars": st.column_config.NumberColumn("PPC propio (ARS)", format="%.2f"),
                "costo_total_ars": st.column_config.NumberColumn("Costo total (ARS)", format="%.2f"),
                "ppc_iol": st.column_config.NumberColumn("PPC IOL (ARS)", format="%.2f"),
            }
        )

        st.subheader("Flujo de caja por símbolo")
        st.dataframe(
            tabla_flujo_caja,
            column_config={
                "monto": st.column_config.NumberColumn("Monto (USD)", format="%.2f"),
            }
        )

        if fechas_fallidas:
            st.warning(f"No se pudo obtener el tipo de cambio para estas fechas: {fechas_fallidas}")

    except Exception as e:
        st.error(f"Tipo de error: {type(e).__name__}")
        st.error(f"Detalle: {e}")
