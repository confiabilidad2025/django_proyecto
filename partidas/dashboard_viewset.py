from viewflow.contrib.plotly import Dashboard
from dash import html

class Partidas_presupuestarias(Dashboard):
    title = "Partidas Presupuestarias"
    label = "OTS"
    icon = "table_chart"
    layout = html.Div([
        html.Iframe(
            src="http://zona1.miteleferico.bo:8090/partidas",
            style={
                "width": "100%",
                "height": "800px",
                "border": "none"
            }
        )
    ])
