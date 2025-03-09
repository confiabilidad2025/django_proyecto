import dash
from dash import html, dcc
import plotly.graph_objs as go
import base64

app = dash.Dash(__name__)

# Codifica la imagen ISO 10816
encoded_image = base64.b64encode(open('img/image.png', 'rb').read()).decode()

app.layout = html.Div(style={'backgroundColor': '#D3D3D3', 'padding': '20px'}, children=[
    dcc.Tabs([
        dcc.Tab(label='Vibración', children=[
            html.Div([
                html.Button('START', style={'width': '300px', 'height': '50px', 'backgroundColor': '#00FF00'}),
                html.Button('STOP', style={'width': '150px', 'height': '50px'}),
            ], style={'display': 'flex', 'gap': '10px'}),

            html.H2('Registro de Vibración GRUPO 1', style={'color': 'red', 'textAlign': 'center'}),

            html.Div([
                html.Button('Grupo 1', id='grupo1', style={'margin-right': '10px'}),
                html.Button('Grupo 2'),
                html.Button('ISO 10816', style={'margin-left': '10px'}),
            ], style={'display': 'flex', 'margin-bottom': '10px'}),

            html.Div([
                html.Button('EJE X', style={'backgroundColor': 'cyan', 'borderRadius': '50%', 'width': '80px', 'height': '80px'}),
                html.Div('AZUL EJE \"X\"', style={'margin-top': '10px', 'color': 'blue'}),
            ], style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center', 'gap': '10px', 'margin-bottom': '10px'}),

            dcc.Graph(
                id='vibration-graph',
                figure={
                    'data': [
                        go.Scatter(
                            x=[],
                            y=[],
                            mode='lines',
                            name='Vibración'
                        )
                    ],
                    'layout': go.Layout(
                        xaxis={'title': 'Tiempo'},
                        yaxis={'title': 'Vibración'},
                        margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                        height=400,
                    )
                }
            ),

            html.Div('10:15:497  20/06/2018', style={'textAlign': 'right', 'margin-top': '-20px'})
        ]),

        dcc.Tab(label='ISO 10816', children=[
            html.Div([
                html.Img(src='data:image/png;base64,{}'.format(encoded_image), style={'width': '100%', 'height': 'auto'}),
                html.Div([
                    html.H3('MOTOR ELECTRICO PRINCIPAL (LINEA MORADA S1)', style={'color': 'blue'}),
                    html.Ul([
                        html.Li('Año: 2018'),
                        html.Li('No. de Fabr.: 2080'),
                        html.Li('Potencia: 1065 kW'),
                        html.Li('Velocidad: 1495 Rpm'),
                        html.Li('Velocidad Embalam.: 1650 Rpm'),
                        html.Li('Altura Piso-Eje \"H\": 450 mm'),                        
                    ])
                ], style={'padding': '20px', 'fontSize': '16px'})
            ], style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center', 'gap': '20px'})
        ])
    ])
])

if __name__ == '__main__':
    app.run_server(debug=True)
