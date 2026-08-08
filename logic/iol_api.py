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
