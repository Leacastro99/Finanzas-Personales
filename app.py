import streamlit as st
from datetime import date, timedelta
from logic.iol_api import (
    obtener_token, obtener_portafolio, obtener_operaciones,
    obtener_cotizaciones_actuales, obtener_series_todas_posiciones
)
from logic.portafolio import portafolio_a_tabla, tabla_resumen_posiciones
from logic.operaciones import (
    operaciones_a_tabla, separar_lotes_y_caja, SIMBOLO_A_SUFIJO_D, agregar_costo_en_ars
)
from logic.fifo import (
    calcular_fifo, calcular_ppc_propio, calcular_resultado_no_realizado,
    calcular_kpis, formatear_moneda
)
from logic.dividendos import resumen_flujo_caja, resultado_neto_por_simbolo
from logic.dolar import obtener_tipos_cambio_por_fecha
from logic.evolucion import series_a_tabla, evolucion_valor_cartera
from logic.graficos import grafico_evolucion_cartera


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

        # ============ CARGA Y CÁLCULO DE DATOS (igual que antes) ============
        portafolio = obtener_portafolio(token)
        tabla_portafolio = portafolio_a_tabla(portafolio)

        operaciones = obtener_operaciones(token, "2023-01-01", "2026-08-08")
        tabla_operaciones = operaciones_a_tabla(operaciones)
        lotes, flujo_caja = separar_lotes_y_caja(tabla_operaciones)

        posiciones, realizado = calcular_fifo(lotes, columna_precio="precio_ajustado")
        ppc_usd = calcular_ppc_propio(posiciones)

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

        tabla_flujo_caja = resumen_flujo_caja(flujo_caja)
        tabla_resultado_neto = resultado_neto_por_simbolo(realizado, tabla_flujo_caja)

        precios_actuales = obtener_cotizaciones_actuales(token, list(posiciones.keys()), SIMBOLO_A_SUFIJO_D)
        tabla_no_realizado = calcular_resultado_no_realizado(posiciones, precios_actuales)

        cantidades_actuales = {s: sum(l["cantidad"] for l in lts) for s, lts in posiciones.items()}
        series_crudas = obtener_series_todas_posiciones(
            token, list(posiciones.keys()), SIMBOLO_A_SUFIJO_D, "2025-08-08", "2026-08-08"
        )
        tabla_series = series_a_tabla(series_crudas)
        evolucion = evolucion_valor_cartera(tabla_series, cantidades_actuales)

        kpis = calcular_kpis(tabla_portafolio, tabla_no_realizado, tabla_resultado_neto, posiciones, precios_actuales)
        tabla_resumen = tabla_resumen_posiciones(posiciones, precios_actuales, ppc_usd, kpis["valor_total_usd"])
        # Sumamos la categoría (tipo de activo) para poder filtrar por ella
        tabla_resumen = tabla_resumen.merge(tabla_portafolio[["simbolo", "tipo"]], on="simbolo", how="left")

        st.success("Conexión con IOL exitosa ✅")

        tab_resumen, tab_detalle = st.tabs(["Resumen", "Detalle"])

        # ============ PESTAÑA RESUMEN ============
        with tab_resumen:
            col_f1, col_f2, col_f3, col_f4 = st.columns(4)
            with col_f1:
                moneda_filtro = st.radio("Moneda", ["USD", "ARS"], horizontal=True)
            with col_f2:
                categoria_filtro = st.selectbox("Categoría", ["Todas"] + sorted(tabla_resumen["tipo"].dropna().unique().tolist()))
            with col_f3:
                activo_filtro = st.selectbox("Activo", ["Todos"] + sorted(tabla_resumen["simbolo"].unique().tolist()))
            with col_f4:
                periodo_filtro = st.selectbox("Período", ["1 mes", "3 meses", "6 meses", "1 año"], index=3)

            # --- Aplicar filtros de categoría y activo ---
            tabla_filtrada = tabla_resumen.copy()
            if categoria_filtro != "Todas":
                tabla_filtrada = tabla_filtrada[tabla_filtrada["tipo"] == categoria_filtro]
            if activo_filtro != "Todos":
                tabla_filtrada = tabla_filtrada[tabla_filtrada["simbolo"] == activo_filtro]

            simbolos_filtrados = tabla_filtrada["simbolo"].tolist()

            valor_cartera_filtrado = tabla_filtrada["valor_usd"].sum()
            no_realizado_filtrado = tabla_no_realizado[tabla_no_realizado["simbolo"].isin(simbolos_filtrados)]["resultado_no_realizado"].sum()
            neto_filtrado = tabla_resultado_neto[tabla_resultado_neto["simbolo"].isin(simbolos_filtrados)]["resultado_neto"].sum()
            resultado_total_filtrado = no_realizado_filtrado + neto_filtrado

            # --- Aplicar filtro de período al gráfico de evolución ---
            dias_por_periodo = {"1 mes": 30, "3 meses": 90, "6 meses": 182, "1 año": 365}
            fecha_desde_periodo = date.today() - timedelta(days=dias_por_periodo[periodo_filtro])
            evolucion_filtrada = evolucion[evolucion["fecha"].dt.date >= fecha_desde_periodo]

            st.caption("Los filtros de arriba afectan a toda esta pestaña.")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Valor cartera", formatear_moneda(valor_cartera_filtrado))
            with col2:
                st.metric("Resultado no realizado", formatear_moneda(no_realizado_filtrado))
            with col3:
                st.metric("Resultado total", formatear_moneda(resultado_total_filtrado))

            st.subheader("Posiciones")
            st.dataframe(
                tabla_filtrada,
                column_config={
                    "simbolo": "Activo",
                    "tipo": "Categoría",
                    "cantidad": st.column_config.NumberColumn("Cantidad", format="%.0f"),
                    "ppc": st.column_config.NumberColumn("PPC (USD)", format="%.2f"),
                    "precio_actual": st.column_config.NumberColumn("Precio actual (USD)", format="%.2f"),
                    "valor_usd": st.column_config.NumberColumn("Valor (USD)", format="%.2f"),
                    "pct_cartera": st.column_config.NumberColumn("% cartera", format="%.1f%%"),
                    "resultado_pct": st.column_config.NumberColumn("Resultado", format="%.1f%%"),
                },
                hide_index=True,
            )

            st.subheader("Evolución del valor de la cartera")
            if not evolucion_filtrada.empty:
                st.plotly_chart(grafico_evolucion_cartera(evolucion_filtrada), use_container_width=True)
            else:
                st.info("No hay datos suficientes para el período seleccionado.")

        # ============ PESTAÑA DETALLE (placeholder por ahora) ============
        with tab_detalle:
            st.info("Acá vamos a construir la comparación vs. SPY con filtro de activo, y el detalle de ganancias/pérdidas — próximo paso.")

    except Exception:
        st.error("No se pudo conectar con IOL. Revisá las credenciales configuradas.")
