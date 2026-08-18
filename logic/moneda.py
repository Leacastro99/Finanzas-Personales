def convertir_a_moneda(valor, moneda, tipo_cambio):
    """Convierte un valor en USD a la moneda elegida, usando el tipo de
    cambio dado. Si la moneda es USD, devuelve el valor sin cambios."""
    if moneda == "ARS" and valor is not None:
        return valor * tipo_cambio
    return valor


def simbolo_moneda(moneda):
    """Símbolo de moneda para mostrar en etiquetas."""
    return "$" if moneda == "ARS" else "U$D"


def formatear_moneda(valor, moneda="USD"):
    """Formatea un valor monetario con precisión adaptativa: sin decimales
    para números grandes, con más decimales a medida que el número es más
    chico. Usado en tarjetas y tablas, donde se muestran valores completos."""
    simbolo = simbolo_moneda(moneda)
    valor_abs = abs(valor)
    if valor_abs >= 1000:
        texto = f"{valor:,.0f}"
    elif valor_abs >= 1:
        texto = f"{valor:,.2f}"
    else:
        texto = f"{valor:,.4f}"
    return f"{simbolo} {texto}"


def formatear_moneda_corta(valor, moneda="USD"):
    """Formatea un valor monetario ABREVIADO (k para miles, M para
    millones). Usado en etiquetas de gráficos, donde el espacio es limitado."""
    simbolo = simbolo_moneda(moneda)
    valor_abs = abs(valor)
    if valor_abs >= 1_000_000:
        texto = f"{valor / 1_000_000:,.2f}M"
    elif valor_abs >= 1_000:
        texto = f"{valor / 1_000:,.1f}k"
    else:
        texto = f"{valor:,.2f}"
    return f"{simbolo} {texto}"


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
