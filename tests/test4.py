import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State
import plotly.graph_objs as go
import base64
import pandas as pd
import numpy as np

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Codifica la imagen ISO 10816
encoded_image = base64.b64encode(open('img/image.png', 'rb').read()).decode()

# Leer datos del CSV
df_motor = pd.read_csv('data/Valores_motor.csv')

def clean_data(df):
    df.columns = df.columns.str.strip()
    df['Timestamp'] = pd.to_timedelta(df['Desviación de Tiempo'], unit='ms')
    df['Timestamp'] = pd.to_datetime(df['Fecha'].astype(str) + ' ' + df['Hora'].astype(str), errors="coerce") + df['Timestamp']
    df = df.drop(columns=['Fecha', 'Hora', 'Desviación de Tiempo', 'Delta(ms)'])
    df = df.dropna(subset=['Valor'])
    df.rename(columns={'Valor': 'X'}, inplace=True)
    np.random.seed(42)
    df['Y'] = df['X'] + np.random.normal(0, 0.05, size=len(df))
    df['Z'] = df['X'] + 9.81
    return df

df_clean = clean_data(df_motor.copy())

def create_iso_fig(rms_value):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[0, 5], y=[0.71, 0.71], fill='tonexty', fillcolor='green', mode='none', name='A'))
    fig.add_trace(go.Scatter(x=[0, 5], y=[2.3, 2.3], fill='tonexty', fillcolor='yellow', mode='none', name='B'))
    fig.add_trace(go.Scatter(x=[0, 5], y=[4.5, 4.5], fill='tonexty', fillcolor='orange', mode='none', name='C'))
    fig.add_trace(go.Scatter(x=[0, 5], y=[12, 12], fill='tonexty', fillcolor='red', mode='none', name='D'))
    fig.add_trace(go.Scatter(x=[2.5], y=[rms_value], mode='markers', marker=dict(size=15, color='blue'), name=f'RMS: {rms_value:.2f} mm/s'))
    fig.update_layout(
        title=' ISO 10816-3',
        xaxis_title='Tiempo (referencial)',
        yaxis_title='Velocidad (mm/s RMS)',
        yaxis=dict(range=[0, 12]),
        xaxis=dict(showticklabels=False),
        plot_bgcolor='white',
        height=400
    )
    return fig

app.layout = dbc.Container(fluid=True, style={'fontFamily': 'Arial Narrow', 'padding': '20px'}, children=[
    dbc.Tabs([
        dbc.Tab(label='Vibración', children=[
            dbc.Card([
                dbc.CardBody([
                    html.H3('Registro de Vibración GRUPO 1', className='text-center text-danger'),
                    dbc.ButtonGroup([
                        dbc.Button('Eje X', id='btn-x', color='primary', n_clicks=0),
                        dbc.Button('Eje Y', id='btn-y', color='secondary', n_clicks=0),
                        dbc.Button('Eje Z', id='btn-z', color='info', n_clicks=0)
                    ], className='mb-3'),

                    dbc.Row([
                        dbc.Col([
                            dcc.Graph(id='iso-graph')
                        ], width=2),

                        dbc.Col([
                            dcc.Graph(id='vibration-graph')
                        ], width=10)
                    ]),

                    html.Div('10:15:497  20/06/2018', className='text-end small text-muted')
                ])
            ])
        ]),

        dbc.Tab(label='ISO 10816', children=[
            dbc.Card([
                dbc.CardBody([
                    html.Img(src='data:image/png;base64,{}'.format(encoded_image), className='img-fluid rounded mb-3 text-center'),
                    dbc.Table([
                        html.Thead(html.Tr([html.Th('Parámetro'), html.Th('Valor')], className='table-primary')),
                        html.Tbody([
                            html.Tr([html.Td('Año'), html.Td('2018')]),
                            html.Tr([html.Td('No. de Fabr.'), html.Td('2080')]),
                            html.Tr([html.Td('Potencia'), html.Td('1065 kW')]),
                            html.Tr([html.Td('Velocidad'), html.Td('1495 Rpm')]),
                            html.Tr([html.Td('Velocidad Embalam.'), html.Td('1650 Rpm')]),
                            html.Tr([html.Td('Altura Piso-Eje "H"'), html.Td('580 mm')]),
                        ])
                    ], bordered=True, hover=True, responsive=True, className='text-center')
                ])
            ])
        ])
    ])
])

@app.callback(
    Output('vibration-graph', 'figure'),
    Output('iso-graph', 'figure'),
    Input('btn-x', 'n_clicks'),
    Input('btn-y', 'n_clicks'),
    Input('btn-z', 'n_clicks')
)
def update_graph(n_x, n_y, n_z):
    ctx = dash.callback_context
    axis = 'X'
    if ctx.triggered:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if button_id == 'btn-y':
            axis = 'Y'
        elif button_id == 'btn-z':
            axis = 'Z'

    valores = df_clean[axis]
    rms = np.sqrt(np.mean(valores ** 2))

    graph_fig = go.Figure(
        data=[go.Scatter(x=df_clean['Timestamp'], y=valores, mode='lines', name=f'Eje {axis}')],
        layout=go.Layout(
            xaxis={'title': 'Tiempo'},
            yaxis={'title': f'Vibración Eje {axis} (mm/s)'},
            height=350,
            margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
            plot_bgcolor='white'
        )
    )

    return graph_fig, create_iso_fig(rms)

if __name__ == '__main__':
    app.run_server(debug=True)
