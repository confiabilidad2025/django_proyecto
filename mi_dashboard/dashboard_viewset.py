from viewflow.contrib.plotly import Dashboard
from django.urls import path

from dash import html
from viewflow.contrib.plotly import Dashboard

class ascensoresDashboard(Dashboard):
    title = "Ascensores"
    label = "Ascensores"
    icon = "elevator"
    app_name = "ascensores"
    layout = html.Div([
        html.Iframe(
            src="http://zona1.miteleferico.bo:8050/",
            style={
                "width": "100%",
                "height": "800px",
                "border": "none"
            }
        )
    ])