import streamlit as st
import pandas as pd
from datetime import date, timedelta
from logic.iol_api import (
    obtener_token, obtener_portafolio, obtener_operaciones,
    obtener_cotizaciones_actuales, obtener_series_todas_posiciones
)
from logic.portafolio import portafolio_a_tabla, tabla_resumen_posiciones
from logic.operaciones import (
    operaciones_a_tabla, separar_lotes_y_caja, SIMBOLO_A_SUFIJO_D, agregar_costo_en_ars
)
from logic.fifo import calcular_fifo, calcular_ppc_propio, calcular_resultado_no_realizado, calcular_kpis
from logic.dividendos import resumen_flujo_caja, resultado_neto_por_simbolo
from logic.dolar import obtener_tipos_cambio_por_fecha, obtener_tipo_cambio_mas_cercano
from logic.evolucion import (
    series_a_tabla, evolucion_valor_cartera,
    cantidad_historica_por_fecha, evolucion_valor_cartera_real
)
from logic.graficos import grafico_evolucion
from logic.moneda import convertir_a_moneda, formatear_moneda, convertir_serie_a_moneda


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

    st.markdown("""
        <style>
        [data-testid="stMetricValue"] {
            font-size: 1.6rem;
            white-space: normal;
            overflow-wrap: break-word;
            line-height: 1.2;
        }
        </style>
    """, unsafe_allow_html=True)

    try:
        token = obtener_token()

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

        kpis = calcular_kpis(tabla_portafolio, tabla_no_realizado, tabla_resultado_neto, posiciones, precios_actuales)
        tabla_resumen = tabla_resumen_posiciones(posiciones, precios_actuales, ppc_usd, kpis["valor_total_usd"])

        fecha_desde_historico = (date.today() - timedelta(days=5 * 365)).strftime("%Y-%m-%d")
        fecha_hasta_historico = date.today().strftime("%Y-%m-%d")
        series_crudas = obtener_series_todas_posiciones(
            token, list(posiciones.keys()), SIMBOLO_A_SUFIJO_D, fecha_desde_historico, fecha_hasta_historico
        )
        tabla_series = series_a_tabla(series_crudas)
        tabla_cantidades_historicas = cantidad_historica_por_fecha(lotes, fecha_desde_historico, fecha_hasta_historico)

        realizado_df = pd.DataFrame(realizado)

        tipo_cambio_hoy = obtener_tipo_cambio_mas_cercano(date.today().strftime("%Y-%m-%d"))

        st.success("Conexión con IOL exitosa ✅")

        tab_resumen, tab_detalle = st.tabs(["Resumen", "Detalle"])

        with tab_resumen:
            col_f1, col_f2, col_f3, col_f4 = st.columns(4)
            with col_f1:
                moneda_filtro = st.radio("Moneda", ["USD", "ARS"], horizontal=True)
            with col_f2:
                categoria_filtro = st.selectbox("Categoría", ["Todas"] + sorted(tabla_portafolio["tipo"].dropna().unique().tolist()))
            with col_f3:
                activo_filtro = st.selectbox("Activo", ["Todos"] + sorted(tabla_resumen["simbolo"].unique().tolist()))
            with col_f4:
                periodo_filtro = st.selectbox(
                    "Período",
                    ["5 años", "3 años", "1 año", "6 meses", "3 meses", "1 mes", "1 semana", "Último día"],
                    index=2
                )

            tabla_filtrada = tabla_resumen.merge(tabla_portafolio[["simbolo", "tipo"]], on="simbolo", how="left")
            if categoria_filtro != "Todas":
                tabla_filtrada = tabla_filtrada[tabla_filtrada["tipo"] == categoria_filtro]
            if activo_filtro != "Todos":
                tabla_filtrada = tabla_filtrada[tabla_filtrada["simbolo"] == activo_filtro]

            simbolos_filtrados = tabla_filtrada["simbolo"].tolist()

            valor_cartera_filtrado = tabla_filtrada["valor_usd"].sum()
            no_realizado_filtrado = tabla_no_realizado[tabla_no_realizado["simbolo"].isin(simbolos_filtrados)]["resultado_no_realizado"].sum()
            realizado_filtrado = realizado_df[realizado_df["simbolo"].isin(simbolos_filtrados)]["resultado"].sum() if not realizado_df.empty else 0
            neto_filtrado = tabla_resultado_neto[tabla_resultado_neto["simbolo"].isin(simbolos_filtrados)]["resultado_neto"].sum()
            resultado_total_filtrado = no_realizado_filtrado + neto_filtrado

            dias_por_periodo = {
                "5 años": 5 * 365, "3 años": 3 * 365, "1 año": 365, "6 meses": 182,
                "3 meses": 90, "1 mes": 30, "1 semana": 7, "Último día": 1
            }
            fecha_desde_periodo = date.today() - timedelta(days=dias_por_periodo[periodo_filtro])

            series_filtradas = tabla_series[
                (tabla_series["simbolo"].isin(simbolos_filtrados)) &
                (tabla_series["fecha"].dt.date >= fecha_desde_periodo)
            ]
            cantidades_hist_filtradas = tabla_cantidades_historicas[
                (tabla_cantidades_historicas["simbolo"].isin(simbolos_filtrados)) &
                (tabla_cantidades_historicas["fecha"].dt.date >= fecha_desde_periodo)
            ]
            cantidades_actuales_filtradas = {
                s: sum(l["cantidad"] for l in posiciones[s]) for s in simbolos_filtrados
            }

            st.caption("Los filtros de arriba afectan a toda esta pestaña.")

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Valor cartera", formatear_moneda(convertir_a_moneda(valor_cartera_filtrado, moneda_filtro, tipo_cambio_hoy), moneda_filtro))
            with col2:
                st.metric("Resultado no realizado", formatear_moneda(convertir_a_moneda(no_realizado_filtrado, moneda_filtro, tipo_cambio_hoy), moneda_filtro))
            with col3:
                st.metric("Resultado realizado", formatear_moneda(convertir_a_moneda(realizado_filtrado, moneda_filtro, tipo_cambio_hoy), moneda_filtro))
            with col4:
                st.metric("Resultado total", formatear_moneda(convertir_a_moneda(resultado_total_filtrado, moneda_filtro, tipo_cambio_hoy), moneda_filtro))

            tabla_mostrar = tabla_filtrada.drop(columns=["tipo"]).copy()
            for columna in ["ppc", "precio_actual", "valor_usd", "resultado_usd"]:
                tabla_mostrar[columna] = tabla_mostrar[columna].apply(
                    lambda v: convertir_a_moneda(v, moneda_filtro, tipo_cambio_hoy)
                )
            etiqueta_moneda = "ARS" if moneda_filtro == "ARS" else "USD"

            st.subheader("Posiciones")
            st.dataframe(
                tabla_mostrar,
                column_config={
                    "simbolo": "Activo",
                    "cantidad": st.column_config.NumberColumn("Cantidad", format="%.0f"),
                    "ppc": st.column_config.NumberColumn(f"PPC ({etiqueta_moneda})", format="%.2f"),
                    "precio_actual": st.column_config.NumberColumn(f"Precio actual ({etiqueta_moneda})", format="%.2f"),
                    "valor_usd": st.column_config.NumberColumn(f"Valor ({etiqueta_moneda})", format="%.2f"),
                    "pct_cartera": st.column_config.NumberColumn("% cartera", format="%.1f%%"),
                    "resultado_usd": st.column_config.NumberColumn(f"Resultado ({etiqueta_moneda})", format="%.2f"),
                    "resultado_pct": st.column_config.NumberColumn("% Resultado", format="%.1f%%"),
                },
                hide_index=True,
            )

            titulo_grafico = activo_filtro if activo_filtro != "Todos" else "Cartera"

            if moneda_filtro == "ARS":
                fechas_evolucion = series_filtradas["fecha"].dt.strftime("%Y-%m-%d")
                tipos_cambio_evolucion, fechas_fallidas_evolucion = obtener_tipos_cambio_por_fecha(fechas_evolucion)
            else:
                tipos_cambio_evolucion, fechas_fallidas_evolucion = {}, []

            evolucion_proy = evolucion_valor_cartera(series_filtradas, cantidades_actuales_filtradas)
            evolucion_proy = convertir_serie_a_moneda(evolucion_proy, moneda_filtro, tipos_cambio_evolucion)

            st.subheader(f"Evolución de {titulo_grafico} — proyección con tenencia actual")
            if not evolucion_proy.empty:
                st.plotly_chart(grafico_evolucion(evolucion_proy, titulo_grafico, moneda_filtro), use_container_width=True)
            else:
                st.info("No hay datos suficientes para el período seleccionado.")

            evolucion_real = evolucion_valor_cartera_real(series_filtradas, cantidades_hist_filtradas)
            evolucion_real = convertir_serie_a_moneda(evolucion_real, moneda_filtro, tipos_cambio_evolucion)

            st.subheader(f"Evolución de {titulo_grafico} — flujo real (según tus compras)")
            if not evolucion_real.empty:
                st.plotly_chart(grafico_evolucion(evolucion_real, titulo_grafico, moneda_filtro), use_container_width=True)
            else:
                st.info("No hay datos suficientes para el período seleccionado.")

            if fechas_fallidas_evolucion:
                st.warning(f"No se pudo obtener el tipo de cambio para algunas fechas del gráfico: {len(fechas_fallidas_evolucion)} días sin dato.")

        with tab_detalle:
            st.info("Acá vamos a construir la comparación vs. SPY con filtro de activo, y el detalle de ganancias/pérdidas — próximo paso.")

    except Exception:
        st.error("No se pudo conectar con IOL. Revisá las credenciales configuradas.")
