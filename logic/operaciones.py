import pandas as pd

MAPEO_SIMBOLOS_D = {
    "AAPLD": "AAPL", "GOGLD": "GOOGL", "MELID": "MELI", "MSFTD": "MSFT",
    "NFLXD": "NFLX", "METAD": "META", "AMZND": "AMZN", "NVDAD": "NVDA",
    "TSLAD": "TSLA", "SPYD": "SPY", "NUD": "NU", "LOMAD": "LOMA",
    "AL29D": "AL29", "YPFDD": "YPFD", "PAMPD": "PAMP", "VISTD": "VIST",
}
SIMBOLO_A_SUFIJO_D = {limpio: sufijo for sufijo, limpio in MAPEO_SIMBOLOS_D.items()}
SIMBOLOS_BONOS = {"AL29"}  # bonos: cotizan cada 100 de valor nominal


def operaciones_a_tabla(operaciones_json):
    """Convierte la lista cruda de operaciones de IOL en una tabla limpia, filtrada y mapeada."""
    tabla = pd.DataFrame(operaciones_json)

    # El estado viene en minúscula ("terminada"), por eso normalizamos con .str.lower()
    tabla = tabla[tabla["estado"].str.lower() == "terminada"].copy()

    # Símbolo limpio (sin sufijo D del segmento dólar)
    tabla["simbolo"] = tabla["simbolo"].replace(MAPEO_SIMBOLOS_D)

    # Ajuste de precio para bonos
    tabla["precio_ajustado"] = tabla.apply(
        lambda fila: fila["precioOperado"] / 100 if fila["simbolo"] in SIMBOLOS_BONOS else fila["precioOperado"],
        axis=1
    )

    return tabla.reset_index(drop=True)


def separar_lotes_y_caja(tabla):
    """Separa filas que son lotes reales (compras, ventas, y dividendos
    pagados en acciones) de las que son puro flujo de caja (dividendos en
    efectivo, renta y amortización de bonos)."""
    es_dividendo_en_acciones = (tabla["tipo"] == "Pago de Dividendos") & (tabla["cantidadOperada"] > 0)
    es_compra_o_venta = tabla["tipo"].isin(["Compra", "Venta"])

    lotes = tabla[es_compra_o_venta | es_dividendo_en_acciones].copy()
    flujo_caja = tabla[~(es_compra_o_venta | es_dividendo_en_acciones)].copy()

    return lotes, flujo_caja
