from viewflow.contrib.plotly import Dashboard
from dash import html

class DashboardOperaciones(Dashboard):
    title = "Dashboard Operaciones"
    label = "operaciones"
    icon = ""
    layout = html.Div([
        html.Iframe(
            src="http://zona1.miteleferico.bo:8090/operaciones",
            style={
                "width": "100%",
                "height": "800px",
                "border": "none"
            }
        )
    ])