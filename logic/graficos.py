import plotly.graph_objects as go
from logic.moneda import formatear_moneda_corta


def grafico_evolucion(evolucion, titulo_serie="Valor", moneda="USD"):
    """Gráfico de evolución con tooltip en cada punto y etiquetas de valor
    solo en los puntos clave: máximo, mínimo y último valor."""
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=evolucion["fecha"], y=evolucion["valor"],
        mode="lines", name=titulo_serie,
        line=dict(color="#1D9E75", width=2),
        hovertemplate="%{x|%d %b %Y}<br>" + formatear_moneda_corta(0, moneda).split()[0] + " %{y:,.2s}<extra></extra>",
    ))

    puntos_clave = {
        "Máximo": evolucion.loc[evolucion["valor"].idxmax()],
        "Mínimo": evolucion.loc[evolucion["valor"].idxmin()],
        "Último": evolucion.iloc[-1],
    }
    for punto in puntos_clave.values():
        fig.add_trace(go.Scatter(
            x=[punto["fecha"]], y=[punto["valor"]],
            mode="markers+text",
            text=[formatear_moneda_corta(punto["valor"], moneda)],
            textposition="top center",
            marker=dict(size=7, color="#1D9E75"),
            showlegend=False,
            hoverinfo="skip",
        ))

    fig.update_layout(
        showlegend=False,
        margin=dict(l=10, r=10, t=10, b=10),
        height=300,
        hovermode="x unified",
    )
    fig.update_yaxes(tickformat="~s")
    return fig
