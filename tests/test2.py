import dash
import dash_bootstrap_components as dbc
from dash import html, dcc
import plotly.graph_objs as go
import base64

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Codifica la imagen ISO 10816
encoded_image = base64.b64encode(open('img/image.png', 'rb').read()).decode()

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

import pandas as pd
df = pd.read_excel('data/Valores 28-10-22 LMO motor TDB.xlsx', sheet_name='Valores Punto1 FO 28-10-22', header=6, usecols='A:E')
df_clean = clean_data(df.copy())
df_clean.head()
#df
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
                            #dbc.Button('EJE X', color='info', className='rounded-circle', style={'width': '80px', 'height': '80px'})                            
                            html.Div('AZUL EJE "X"', className='mt-2 text-info text-center')
                        ], width=2),

                        dbc.Col([
                            dcc.Graph(
                                id='vibration-graph',
                                figure={
                                    'data': [
                                        go.Scatter(x=df_clean['Timestamp'], y=df_clean['Valor'], mode='lines', name='Valor Acelerometro')
                                        #go.Scatter(x=[], y=[], mode='lines', name='Vibración', line={'color': '#1f77b4'})
                                    ],
                                    'layout': go.Layout(
                                        title="",
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
