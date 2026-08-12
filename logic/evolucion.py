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
    """Calcula la evolución del valor total de la cartera día a día."""
    tabla = tabla_series.copy()
    tabla["cantidad"] = tabla["simbolo"].map(cantidades_actuales)
    tabla["valor"] = tabla["precio"] * tabla["cantidad"]
    return tabla.groupby("fecha")["valor"].sum().reset_index()
