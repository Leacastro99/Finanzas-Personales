import requests


def obtener_tipo_cambio(fecha, casa="contadoconliqui"):
    """Trae la cotización del dólar (MEP o CCL) para una fecha puntual,
    usando la API pública de ArgentinaDatos. fecha en formato 'AAAA-MM-DD'."""
    fecha_formateada = fecha.replace("-", "/")
    url = f"https://api.argentinadatos.com/v1/cotizaciones/dolares/{casa}/{fecha_formateada}"
    respuesta = requests.get(url)
    respuesta.raise_for_status()
    return respuesta.json()
