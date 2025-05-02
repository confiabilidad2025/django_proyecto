from viewflow.contrib.plotly import Dashboard
from dash import html

class IndicadoresTorres(Dashboard):
    title = "Indicadores Torres"
    label = "indicadores"
    icon = "pie_chart"
    layout = html.Div([
        html.Iframe(
            src="http://zona1.miteleferico.bo:8090/indicadoresDeTorres",
            style={
                "width": "100%",
                "height": "800px",
                "border": "none"
            }
        )
    ])