from viewflow.contrib.plotly import Dashboard
from dash import html

class IndicadoresPreventivos(Dashboard):
    title = "Indicadores Preventivos"
    label = "indicadores"
    icon = "pie_chart"
    layout = html.Div([
        html.Iframe(
            src="http://zona1.miteleferico.bo:8090/linearoja",
            style={
                "width": "100%",
                "height": "800px",
                "border": "none"
            }
        )
    ])