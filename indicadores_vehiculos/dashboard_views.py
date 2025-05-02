from viewflow.contrib.plotly import Dashboard
from dash import html

class IndicadoresVehiculos(Dashboard):
    title = "Indicadores Vehiculos"
    label = "indicadores"
    icon = "pie_chart"
    layout = html.Div([
        html.Iframe(
            src="http://zona1.miteleferico.bo:8090/indicadoresDeVehiculos",
            style={
                "width": "100%",
                "height": "800px",
                "border": "none"
            }
        )
    ])