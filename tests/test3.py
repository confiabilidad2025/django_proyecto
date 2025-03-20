
import dash
import dash_bootstrap_components as dbc
from dash import html, dcc
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
    # Limpiar nombres de columnas eliminando espacios adicionales
    df.columns = df.columns.str.strip()
    # TypeError: unsupported operand type(s) for +: 'DatetimeArray' and 'str'
    df['Timestamp'] = pd.to_timedelta(df['Desviación de Tiempo'], unit='ms')
    df['Timestamp'] = pd.to_datetime(df['Fecha'].astype(str) + ' ' + df['Hora'].astype(str),errors="coerce") + df['Timestamp']
    # Remove columns Fecha, Hora, and Desviación de Tiempo
    df = df.drop(columns=['Fecha', 'Hora', 'Desviación de Tiempo','Delta(ms)'])
    # Eliminar filas con valores nulos en 'Valor'
    df = df.dropna(subset=['Valor'])
    return df

# Limpieza y conversión de datos
#df_motor['Timestamp'] = pd.to_datetime(df_motor['Timestamp'])
#valores_motor = df_motor['Valor']
df_clean = clean_data(df_motor.copy())
#df_clean.head()
valores_motor = df_clean['Valor']

# Calcular RMS
velocidad_rms = np.sqrt(np.mean(valores_motor ** 2))

# Crear gráfica ISO 10816-3
iso_fig = go.Figure()
iso_fig.add_trace(go.Scatter(x=[0, 5], y=[0.71, 0.71], fill='tonexty', fillcolor='green', mode='none', name='A'))
iso_fig.add_trace(go.Scatter(x=[0, 5], y=[2.3, 2.3], fill='tonexty', fillcolor='yellow', mode='none', name='B'))
iso_fig.add_trace(go.Scatter(x=[0, 5], y=[4.5, 4.5], fill='tonexty', fillcolor='orange', mode='none', name='C'))
iso_fig.add_trace(go.Scatter(x=[0, 5], y=[12, 12], fill='tonexty', fillcolor='red', mode='none', name='D'))
iso_fig.add_trace(go.Scatter(x=[2.5], y=[velocidad_rms], mode='markers', marker=dict(size=15, color='blue'), name=f'RMS: {velocidad_rms:.2f} mm/s'))
iso_fig.update_layout(
    title=' ISO 10816-3',
    xaxis_title='Tiempo (referencial)',
    yaxis_title='Velocidad (mm/s RMS)',
    yaxis=dict(range=[0, 12]),
    xaxis=dict(showticklabels=False),
    plot_bgcolor='white',
    height=400
)

app.layout = dbc.Container(fluid=True, style={'fontFamily': 'Arial Narrow', 'padding': '20px'}, children=[
    dbc.Tabs([
        dbc.Tab(label='Vibración', children=[
            dbc.Card([
                dbc.CardBody([
                    html.H3('Registro de Vibración GRUPO 1', className='text-center text-danger'),
                    dbc.ButtonGroup([
                        dbc.Button('Eje X', color='primary'),
                        dbc.Button('Eje Y', color='secondary'),
                        dbc.Button('Eje Z', color='info')
                    ], className='mb-3'),

                    dbc.Row([


                        dbc.Col([
                            #html.Div('AZUL EJE "X"', className='mt-2 text-info text-center'),
                            dcc.Graph(figure=iso_fig),
                        ], width=2),

                        dbc.Col([
                            dcc.Graph(
                                id='vibration-graph',
                                figure={
                                    'data': [go.Scatter(x=df_clean['Timestamp'], y=valores_motor, mode='lines', name='Valor Acelerometro')],
                                    'layout': go.Layout(
                                        xaxis={'title': 'Tiempo', 'showgrid': False},
                                        yaxis={'title': 'Vibración (mm/s)', 'showgrid': True},
                                        height=350,
                                        margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                                        plot_bgcolor='white'
                                    )
                                }
                            )
                        ], width=10)
                    ]),

                    html.Div('10:15:497  20/06/2018', className='text-end small text-muted')
                ])
            ])
        ]),

        dbc.Tab(label='ISO 10816', children=[
            dbc.Card([
                dbc.CardBody([
                    #dcc.Graph(figure=iso_fig),
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

if __name__ == '__main__':
    app.run_server(debug=True)
