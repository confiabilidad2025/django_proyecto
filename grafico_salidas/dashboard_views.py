from viewflow.contrib.plotly import Dashboard
from dash import html

class GraficoSalidas(Dashboard):
    title = "Grafico Salidas"
    label = "grafico salidas"
    icon = "show_chart"
    layout = html.Div([
        html.Iframe(
            src="http://zona1.miteleferico.bo:8090/grafico_salida",
            style={
                "width": "100%",
                "height": "800px",
                "border": "none"
            }
        )
    ])
