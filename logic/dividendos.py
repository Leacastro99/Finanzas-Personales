def limpiar_simbolo_caja(simbolo):
    """Quita el sufijo ' US$' que usa IOL para distinguir la pata en dólares
    de un movimiento de caja (dividendos, renta, amortización)."""
    return simbolo.replace(" US$", "")


def resumen_flujo_caja(flujo_caja):
    """Resume el flujo de caja (dividendos en efectivo, renta, amortización)
    por símbolo y tipo de movimiento, quedándonos solo con la pata en dólares
    (la que trae el monto real) para evitar contar cada movimiento dos veces."""
    caja_usd = flujo_caja[flujo_caja["montoOperado"].notna()].copy()
    caja_usd["simbolo"] = caja_usd["simbolo"].apply(limpiar_simbolo_caja)
    caja_usd["moneda"] = "USD"

    resumen = (
        caja_usd
        .groupby(["simbolo", "tipo", "moneda"])["montoOperado"]
        .sum()
        .reset_index()
        .rename(columns={"montoOperado": "monto"})
    )
    return resumen
