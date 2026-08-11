import requests

def obtener_tipo_cambio(fecha, casa="contadoconliqui"):
    """Trae la cotización del dólar (MEP o CCL) para una fecha puntual,
    usando la API pública de ArgentinaDatos. fecha en formato 'AAAA-MM-DD'."""
    fecha_formateada = fecha.replace("-", "/")
    url = f"https://api.argentinadatos.com/v1/cotizaciones/dolares/{casa}/{fecha_formateada}"
    respuesta = requests.get(url)
    respuesta.raise_for_status()
    return respuesta.json()

def obtener_tipos_cambio_por_fecha(fechas, casa="contadoconliqui"):
    """Trae el tipo de cambio de venta para cada fecha única de una lista,
    evitando pedir el mismo día más de una vez."""
    fechas_unicas = set(fechas)
    tipos_cambio = {}
    for fecha in fechas_unicas:
        datos = obtener_tipo_cambio(fecha, casa)
        tipos_cambio[fecha] = datos["venta"]
    return tipos_cambio
