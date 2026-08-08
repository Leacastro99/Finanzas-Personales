def calcular_fifo(lotes):
    """
    Aplica FIFO por símbolo sobre los lotes (compras, ventas y dividendos
    en acciones). Devuelve:
      - posiciones: dict {simbolo: [lotes abiertos]} -> lo que aún tenés
      - realizado: lista de resultados de cada venta, calculados contra
        los lotes más antiguos primero
    """
    lotes = lotes.sort_values("order_date")
    posiciones = {}
    realizado = []

    for _, fila in lotes.iterrows():
        simbolo = fila["simbolo"]
        posiciones.setdefault(simbolo, [])

        if fila["type"] == "Compra":
            posiciones[simbolo].append({
                "cantidad": fila["quantity"],
                "precio": fila["precio_ajustado"],
            })

        elif fila["type"] == "Pago de Dividendos":
            # Dividendo en acciones = lote de costo cero
            posiciones[simbolo].append({
                "cantidad": fila["quantity"],
                "precio": 0.0,
            })

        elif fila["type"] == "Venta":
            cantidad_a_vender = fila["quantity"]
            precio_venta = fila["precio_ajustado"]

            while cantidad_a_vender > 0 and posiciones[simbolo]:
                lote = posiciones[simbolo][0]
                cantidad_del_lote = min(cantidad_a_vender, lote["cantidad"])

                resultado = cantidad_del_lote * (precio_venta - lote["precio"])
                realizado.append({
                    "simbolo": simbolo,
                    "fecha": fila["order_date"],
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
