import pandas as pd

def calcular_fifo(lotes):
    """Aplica FIFO por símbolo sobre los lotes. Devuelve posiciones abiertas y resultado realizado."""
    lotes = lotes.sort_values("fechaOperada")
    posiciones = {}
    realizado = []

    for _, fila in lotes.iterrows():
        simbolo = fila["simbolo"]
        posiciones.setdefault(simbolo, [])

        if fila["tipo"] == "Compra":
            posiciones[simbolo].append({
                "cantidad": fila["cantidadOperada"],
                "precio": fila["precio_ajustado"],
            })

        elif fila["tipo"] == "Pago de Dividendos":
            posiciones[simbolo].append({
                "cantidad": fila["cantidadOperada"],
                "precio": 0.0,
            })

        elif fila["tipo"] == "Venta":
            cantidad_a_vender = fila["cantidadOperada"]
            precio_venta = fila["precio_ajustado"]

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
    """Calcula el PPC propio (promedio ponderado) a partir de los lotes FIFO abiertos."""
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
        })
    return pd.DataFrame(filas)
