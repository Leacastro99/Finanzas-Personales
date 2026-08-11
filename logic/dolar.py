import requests
import streamlit as st
from datetime import datetime, timedelta


@st.cache_data(ttl=86400)  # el tipo de cambio de un día no cambia, cacheamos 24hs
def obtener_tipo_cambio(fecha, casa="contadoconliqui"):
    """Trae la cotización del dólar (MEP o CCL) para una fecha puntual,
    usando la API pública de ArgentinaDatos. fecha en formato 'AAAA-MM-DD'."""
    fecha_formateada = fecha.replace("-", "/")
    url = f"https://api.argentinadatos.com/v1/cotizaciones/dolares/{casa}/{fecha_formateada}"
    respuesta = requests.get(url)
    respuesta.raise_for_status()
    return respuesta.json()


def obtener_tipo_cambio_mas_cercano(fecha, casa="contadoconliqui", max_dias_atras=7):
    """Busca el tipo de cambio de la fecha exacta. Si no hay dato (fin de
    semana, feriado, error temporal), retrocede día a día hasta encontrar
    el más cercano disponible."""
    fecha_dt = datetime.strptime(fecha, "%Y-%m-%d")
    for dias_atras in range(max_dias_atras + 1):
        fecha_intento = (fecha_dt - timedelta(days=dias_atras)).strftime("%Y-%m-%d")
        try:
            datos = obtener_tipo_cambio(fecha_intento, casa)
            return datos["venta"]
        except Exception:
            continue
    return None


def obtener_tipos_cambio_por_fecha(fechas, casa="contadoconliqui"):
    """Trae el tipo de cambio de venta para cada fecha única de una lista,
    usando el más cercano disponible cuando falta la fecha exacta."""
    fechas_unicas = set(fechas)
    tipos_cambio = {}
    fechas_fallidas = []

    for fecha in fechas_unicas:
        valor = obtener_tipo_cambio_mas_cercano(fecha, casa)
        if valor is not None:
            tipos_cambio[fecha] = valor
        else:
            fechas_fallidas.append(fecha)

    return tipos_cambio, fechas_fallidas
