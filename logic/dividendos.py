import pandas as pd

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

def resultado_neto_por_simbolo(realizado, tabla_flujo_caja):
    """Combina resultado de capital (FIFO) con flujo de caja (dividendos,
    renta, amortización) por símbolo. Devuelve ambos componentes por
    separado más la suma, sin perder la trazabilidad de cada uno."""
    realizado_df = pd.DataFrame(realizado)
    if realizado_df.empty:
        capital_por_simbolo = pd.DataFrame(columns=["simbolo", "resultado_capital"])
    else:
        capital_por_simbolo = (
            realizado_df.groupby("simbolo")["resultado"]
            .sum()
            .reset_index()
            .rename(columns={"resultado": "resultado_capital"})
        )

    caja_por_simbolo = (
        tabla_flujo_caja.groupby("simbolo")["monto"]
        .sum()
        .reset_index()
        .rename(columns={"monto": "flujo_caja_cobrado"})
    )

    resumen = capital_por_simbolo.merge(caja_por_simbolo, on="simbolo", how="outer").fillna(0)
    resumen["resultado_neto"] = resumen["resultado_capital"] + resumen["flujo_caja_cobrado"]
    resumen["moneda"] = "USD"

    return resumen.sort_values("simbolo").reset_index(drop=True)
