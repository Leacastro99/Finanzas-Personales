import pandas as pd

MAPEO_SIMBOLOS_D = {
    "AAPLD": "AAPL", "GOGLD": "GOOGL", "MELID": "MELI", "MSFTD": "MSFT",
    "NFLXD": "NFLX", "METAD": "META", "AMZND": "AMZN", "NVDAD": "NVDA",
    "TSLAD": "TSLA", "SPYD": "SPY", "NUD": "NU", "LOMAD": "LOMA",
    "AL29D": "AL29", "YPFDD": "YPFD", "PAMPD": "PAMP", "VISTD": "VIST",
}


def operaciones_a_tabla(operaciones_json):
    """Convierte el JSON crudo de operaciones en una tabla limpia, filtrada y mapeada."""
    tabla = pd.DataFrame(operaciones_json["operations"])

    # Solo operaciones efectivamente concretadas
    tabla = tabla[tabla["status"] == "Terminada"].copy()

    # Símbolo limpio (sin sufijo D del segmento dólar)
    tabla["simbolo"] = tabla["symbol"].replace(MAPEO_SIMBOLOS_D)

    # Ajuste de precio para bonos: cotizan cada 100 de valor nominal
    tabla["precio_ajustado"] = tabla.apply(
        lambda fila: fila["price"] / 100 if fila["asset_type"] == "GOVERNMENT_BONDS" else fila["price"],
        axis=1
    )

    return tabla.reset_index(drop=True)


def separar_lotes_y_caja(tabla):
    """Separa las filas que son lotes reales (compras/ventas/dividendos en
    acciones) de las que son puro movimiento de caja (dividendos en efectivo,
    renta, amortización)."""
    lotes = tabla[tabla["quantity"] > 0].copy()
    flujo_caja = tabla[tabla["quantity"] == 0].copy()
    return lotes, flujo_caja
