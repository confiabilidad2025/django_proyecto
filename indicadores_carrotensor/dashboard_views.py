from viewflow.contrib.plotly import Dashboard
from dash import html

class IndicadoresCarroTensor(Dashboard):
    title = "Indicadores Carro Tensor"
    label = "indicadores"
    icon = "show_chart"
    layout = html.Div([
        html.Iframe(
            src="http://zona1.miteleferico.bo:8090/carroTensor",
            style={
                "width": "100%",
                "height": "800px",
                "border": "none"
            }
        )
    ])