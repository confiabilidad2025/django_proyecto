from viewflow.contrib.plotly import Dashboard
from django.urls import path
from .views import GraficoIngresoIframeView

from dash import html

class GraficoIframeDashboard(Dashboard):
    title = "Gráfico de Ingreso"
    label="Grafico"
    icon = "timeline"
    layout = html.Div([
        html.Iframe(
            src="http://zona1.miteleferico.bo:8090/grafico_ingreso",
            style={
                "width": "100%",
                "height": "800px",
                "border": "none"
            }
        )
    ])
