def convertir_serie_a_moneda(tabla_valor, moneda, tipos_cambio_por_fecha):
    """Convierte una serie con columnas 'fecha' y 'valor' a la moneda
    elegida, usando el tipo de cambio HISTÓRICO de cada fecha puntual —
    nunca un tipo de cambio único aplicado a todo el rango."""
    if moneda != "ARS":
        return tabla_valor
    tabla = tabla_valor.copy()
    tabla["fecha_str"] = tabla["fecha"].dt.strftime("%Y-%m-%d")
    tabla["tipo_cambio"] = tabla["fecha_str"].map(tipos_cambio_por_fecha)
    tabla["valor"] = tabla["valor"] * tabla["tipo_cambio"]
    return tabla.drop(columns=["fecha_str", "tipo_cambio"])
