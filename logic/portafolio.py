import pandas as pd

def portafolio_a_tabla(portafolio_json):
    """Convierte el JSON crudo del portafolio de IOL en una tabla (DataFrame)."""
    filas = []
    for activo in portafolio_json["activos"]:
        filas.append({
            "simbolo": activo["titulo"]["simbolo"],
            "descripcion": activo["titulo"]["descripcion"],
            "tipo": activo["titulo"]["tipo"],
            "moneda": activo["titulo"]["moneda"],
            "cantidad": activo["cantidad"],
            "ppc_iol": activo["ppc"],
            "ultimo_precio": activo["ultimoPrecio"],
            "valorizado": activo["valorizado"],
            "ganancia_dinero": activo["gananciaDinero"],
            "ganancia_porcentaje": activo["gananciaPorcentaje"],
        })
    return pd.DataFrame(filas)
