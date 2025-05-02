from viewflow.contrib.plotly import Dashboard
from dash import html

class DashboardOts(Dashboard):
    title = "Dashboard OTS"
    label = "OTS"
    icon = "bar_chart"
    layout = html.Div([
        html.Iframe(
            src="http://zona1.miteleferico.bo:8090/dashboard",
            style={
                "width": "100%",
                "height": "800px",
                "border": "none"
            }
        )
    ])

