import requests
import streamlit as st

def obtener_token():
    """Autentica contra la API de IOL y devuelve el token de acceso."""
    url = "https://api.invertironline.com/token"
    datos = {
        "username": st.secrets["IOL_USER"],
        "password": st.secrets["IOL_PASSWORD"],
        "grant_type": "password"
    }
    respuesta = requests.post(url, data=datos)
    respuesta.raise_for_status()
    return respuesta.json()["access_token"]


def obtener_portafolio(token):
    """Trae la tenencia actual de la cuenta desde la API de IOL."""
    url = "https://api.invertironline.com/api/v2/portafolio/argentina"
    headers = {"Authorization": f"Bearer {token}"}
    respuesta = requests.get(url, headers=headers)
    respuesta.raise_for_status()
    return respuesta.json()


def obtener_operaciones(token, fecha_desde, fecha_hasta):
    """Trae el historial de operaciones desde la API de IOL."""
    url = "https://api.invertironline.com/api/v2/operaciones"
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "filtro.fechaDesde": fecha_desde,
        "filtro.fechaHasta": fecha_hasta,
        "filtro.estado": "terminadas",
        "filtro.pais": "argentina",
    }
    respuesta = requests.get(url, headers=headers, params=params)
    respuesta.raise_for_status()
    return respuesta.json()

def obtener_estado_cuenta(token):
    """Trae el estado de cuenta, que incluye movimientos como dividendos, renta y amortizaciones."""
    url = "https://api.invertironline.com/api/v2/estadocuenta"
    headers = {"Authorization": f"Bearer {token}"}
    respuesta = requests.get(url, headers=headers)
    respuesta.raise_for_status()
    return respuesta.json()
