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


def tabla_resumen_posiciones(posiciones, precios_actuales, ppc_usd, valor_total_usd):
    """Arma la tabla principal del dashboard: una fila por posición abierta,
    con cantidad, PPC, precio actual, % que representa sobre el total, y
    resultado no realizado en porcentaje."""
    filas = []
    for simbolo, lotes in posiciones.items():
        cantidad = sum(lote["cantidad"] for lote in lotes)
        if cantidad == 0:
            continue
        precio_actual = precios_actuales.get(simbolo)
        if precio_actual is None:
            continue

        ppc_fila = ppc_usd[ppc_usd["simbolo"] == simbolo]
        ppc = ppc_fila["ppc_propio"].iloc[0] if not ppc_fila.empty else None

        valor_posicion = cantidad * precio_actual
        resultado_pct = ((precio_actual - ppc) / ppc * 100) if ppc else None

        filas.append({
            "simbolo": simbolo,
            "cantidad": cantidad,
            "ppc": ppc,
            "precio_actual": precio_actual,
            "valor_usd": valor_posicion,
            "pct_cartera": (valor_posicion / valor_total_usd * 100) if valor_total_usd else 0,
            "resultado_pct": resultado_pct,
        })

    return pd.DataFrame(filas).sort_values("pct_cartera", ascending=False).reset_index(drop=True)
