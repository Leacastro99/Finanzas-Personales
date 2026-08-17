import pandas as pd


def series_a_tabla(series_por_simbolo):
    """Convierte el diccionario de series históricas crudas en una tabla
    larga (una fila por símbolo y fecha)."""
    filas = []
    for simbolo, registros in series_por_simbolo.items():
        for registro in registros:
            filas.append({
                "simbolo": simbolo,
                "fecha": registro["fechaHora"][:10],
                "precio": registro["ultimoPrecio"],
            })
    tabla = pd.DataFrame(filas)
    tabla["fecha"] = pd.to_datetime(tabla["fecha"])
    return tabla.sort_values(["simbolo", "fecha"]).reset_index(drop=True)


def evolucion_valor_cartera(tabla_series, cantidades_actuales):
    """'Proyección': valor de la cartera si siempre hubieras tenido la
    cantidad ACTUAL de cada activo (no contempla cuándo compraste)."""
    tabla = tabla_series.copy()
    tabla["cantidad"] = tabla["simbolo"].map(cantidades_actuales)
    tabla["valor"] = tabla["precio"] * tabla["cantidad"]
    return tabla.groupby("fecha")["valor"].sum().reset_index()


def cantidad_historica_por_fecha(lotes, fecha_desde, fecha_hasta):
    """Calcula la cantidad REAL tenida de cada símbolo, día a día, a partir
    del historial de compras, ventas y dividendos en acciones."""
    movimientos = lotes.copy()
    movimientos["fecha"] = pd.to_datetime(movimientos["fechaOperada"].str[:10])
    movimientos["signo"] = movimientos["tipo"].map({
        "Compra": 1, "Pago de Dividendos": 1, "Venta": -1
    })
    movimientos["cantidad_firmada"] = movimientos["cantidadOperada"] * movimientos["signo"]

    rango_fechas = pd.date_range(fecha_desde, fecha_hasta, freq="D")
    filas = []

    for simbolo in movimientos["simbolo"].unique():
        mov_simbolo = movimientos[movimientos["simbolo"] == simbolo]
        cantidad_por_dia = mov_simbolo.groupby("fecha")["cantidad_firmada"].sum()
        serie_diaria = cantidad_por_dia.reindex(rango_fechas, fill_value=0).cumsum()
        for fecha, cantidad in serie_diaria.items():
            filas.append({"simbolo": simbolo, "fecha": fecha, "cantidad": cantidad})

    return pd.DataFrame(filas)


def evolucion_valor_cartera_real(tabla_series, tabla_cantidades_historicas):
    """'Flujo real': valor de la cartera día a día, usando la cantidad que
    REALMENTE tenías de cada activo en cada fecha (refleja tus compras
    progresivas, no una cantidad fija)."""
    combinado = tabla_series.merge(
        tabla_cantidades_historicas, on=["simbolo", "fecha"], how="inner"
    )
    combinado["valor"] = combinado["precio"] * combinado["cantidad"]
    return combinado.groupby("fecha")["valor"].sum().reset_index()
