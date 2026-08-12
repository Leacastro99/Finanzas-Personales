import pandas as pd


def calcular_fifo(lotes, columna_precio="precio_ajustado"):
    """
    Aplica FIFO por símbolo. `columna_precio` indica qué columna de precio
    usar (por ejemplo 'precio_ajustado' para USD o 'precio_ajustado_ars'
    para pesos), así la misma función sirve para cualquier moneda.
    """
    lotes = lotes.sort_values("fechaOperada")
    posiciones = {}
    realizado = []

    for _, fila in lotes.iterrows():
        simbolo = fila["simbolo"]
        posiciones.setdefault(simbolo, [])

        if fila["tipo"] == "Compra":
            posiciones[simbolo].append({
                "cantidad": fila["cantidadOperada"],
                "precio": fila[columna_precio],
            })

        elif fila["tipo"] == "Pago de Dividendos":
            posiciones[simbolo].append({
                "cantidad": fila["cantidadOperada"],
                "precio": 0.0,
            })

        elif fila["tipo"] == "Venta":
            cantidad_a_vender = fila["cantidadOperada"]
            precio_venta = fila[columna_precio]

            while cantidad_a_vender > 0 and posiciones[simbolo]:
                lote = posiciones[simbolo][0]
                cantidad_del_lote = min(cantidad_a_vender, lote["cantidad"])

                resultado = cantidad_del_lote * (precio_venta - lote["precio"])
                realizado.append({
                    "simbolo": simbolo,
                    "fecha": fila["fechaOperada"],
                    "cantidad": cantidad_del_lote,
                    "precio_compra": lote["precio"],
                    "precio_venta": precio_venta,
                    "resultado": resultado,
                })

                lote["cantidad"] -= cantidad_del_lote
                cantidad_a_vender -= cantidad_del_lote
                if lote["cantidad"] == 0:
                    posiciones[simbolo].pop(0)

    return posiciones, realizado


def calcular_ppc_propio(posiciones):
    """Calcula el PPC propio (promedio ponderado) y el costo total a partir
    de los lotes FIFO abiertos."""
    filas = []
    for simbolo, lotes_abiertos in posiciones.items():
        cantidad_total = sum(lote["cantidad"] for lote in lotes_abiertos)
        if cantidad_total == 0:
            continue
        costo_total = sum(lote["cantidad"] * lote["precio"] for lote in lotes_abiertos)
        filas.append({
            "simbolo": simbolo,
            "cantidad_fifo": cantidad_total,
            "ppc_propio": costo_total / cantidad_total,
            "costo_total": costo_total,
        })
    return pd.DataFrame(filas)


def calcular_resultado_no_realizado(posiciones, precios_actuales):
    """Calcula el resultado no realizado comparando el PPC propio contra
    el precio actual de mercado, para cada posición abierta."""
    filas = []
    for simbolo, lotes_abiertos in posiciones.items():
        cantidad_total = sum(lote["cantidad"] for lote in lotes_abiertos)
        if cantidad_total == 0:
            continue
        costo_total = sum(lote["cantidad"] * lote["precio"] for lote in lotes_abiertos)
        ppc_propio = costo_total / cantidad_total
        precio_actual = precios_actuales.get(simbolo)
        if precio_actual is None:
            continue

        filas.append({
            "simbolo": simbolo,
            "cantidad": cantidad_total,
            "ppc_propio": ppc_propio,
            "precio_actual": precio_actual,
            "resultado_no_realizado": (precio_actual - ppc_propio) * cantidad_total,
            "moneda": "USD",
        })
    return pd.DataFrame(filas)


def calcular_kpis(tabla_portafolio, tabla_no_realizado, tabla_resultado_neto, posiciones, precios_actuales):
    """Arma los números resumen para las tarjetas de KPI."""
    valor_total_ars = tabla_portafolio["valorizado"].sum()
    valor_total_usd = sum(
        sum(lote["cantidad"] for lote in lotes) * precios_actuales.get(simbolo, 0)
        for simbolo, lotes in posiciones.items()
    )
    return {
        "valor_total_ars": valor_total_ars,
        "valor_total_usd": valor_total_usd,
        "resultado_no_realizado_usd": tabla_no_realizado["resultado_no_realizado"].sum(),
        "resultado_neto_usd": tabla_resultado_neto["resultado_neto"].sum(),
    }


def formatear_moneda(valor, simbolo_moneda="U$D"):
    """Formatea un valor monetario con precisión adaptativa: sin decimales
    para números grandes, con más decimales a medida que el número es más
    chico (precios de acciones bajas, centavos)."""
    valor_abs = abs(valor)
    if valor_abs >= 1000:
        texto = f"{valor:,.0f}"
    elif valor_abs >= 1:
        texto = f"{valor:,.2f}"
    else:
        texto = f"{valor:,.4f}"
    return f"{simbolo_moneda} {texto}"
