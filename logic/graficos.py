import plotly.graph_objects as go


def grafico_evolucion_cartera(evolucion):
    """Gráfico de evolución con tooltip en cada punto y etiquetas de valor
    solo en los puntos clave: máximo, mínimo y último valor."""
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=evolucion["fecha"], y=evolucion["valor"],
        mode="lines", name="Valor cartera",
        line=dict(color="#1D9E75", width=2),
        hovertemplate="%{x|%d %b %Y}<br>U$D %{y:,.0f}<extra></extra>",
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
            text=[f"U$D {punto['valor']:,.0f}"],
            textposition="top center",
            marker=dict(size=7, color="#1D9E75"),
            showlegend=False,
            hoverinfo="skip",
        ))

    fig.update_layout(
        showlegend=False,
        margin=dict(l=10, r=10, t=10, b=10),
        height=320,
        hovermode="x unified",
    )
    return fig
