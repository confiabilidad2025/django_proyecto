from viewflow.contrib.plotly import Dashboard
from dash import html

class IndicadoresAvance(Dashboard):
    title = "Indicadores Avance"
    label = "indicadores"
    icon = "bar_chart"
    layout = html.Div([
        html.Iframe(
            src="http://zona1.miteleferico.bo:8090/indicadoresSemestre",
            style={
                "width": "100%",
                "height": "800px",
                "border": "none"
            }
        )
    ])