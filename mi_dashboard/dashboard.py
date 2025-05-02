# mi_dashboard/dashboard.py
import dash
from dash import dcc, html, Input, Output
from dash import dash_table
import mysql.connector
import pandas as pd
import plotly.express as px
from datetime import date
import os
#from dash import callback
from viewflow.contrib.plotly import Dashboard, material

px.defaults.template = "plotly_white"


# Configuración de conexión a MySQL (mantener fuera del layout)
host = "192.168.100.60"
user = "zona1"
password = "Sistemas0."
database = "opmt2"

# Ruta del archivo Excel
ruta_excel = os.path.join(os.path.dirname(__file__), "estacionestado.xlsx")
if not os.path.exists(ruta_excel):
    raise FileNotFoundError(f"No se encontró el archivo: {ruta_excel}")

# Función para obtener datos de MySQL
def obtener_datos_mysql():
    try:
        conexion = mysql.connector.connect(host=host, user=user, password=password, database=database)
        cursor = conexion.cursor()
        query = """
            SELECT a.nestacion, a.linea, a.codigo_asc, a.fecha_inicial, a.fecha_final, a.observaciones
            FROM ascensores a
            INNER JOIN (
                SELECT nestacion, linea, codigo_asc, MAX(fecha_inicial) AS ultima_fecha
                FROM ascensores
                WHERE tipo_mant = 'interrupcion' AND YEAR(fecha_inicial) = 2025
                GROUP BY nestacion, linea, codigo_asc
            ) ult
            ON a.codigo_asc = ult.codigo_asc
            AND a.nestacion = ult.nestacion
            AND a.linea = ult.linea
            AND a.fecha_inicial = ult.ultima_fecha
            ORDER BY a.linea, a.nestacion, a.codigo_asc;
        """
        cursor.execute(query)
        resultados = cursor.fetchall()
        df_sql = pd.DataFrame(resultados, columns=["nestacion", "linea", "codigo_asc", "fecha_inicial", "fecha_final", "observaciones"])
        df_sql["Estado"] = df_sql["fecha_final"].apply(lambda x: "Inoperativo" if pd.isna(x) or x == "" else "Operativo")
        return df_sql
    except mysql.connector.Error as err:
        print(f"Error de conexión a la base de datos: {err}")
        return pd.DataFrame()
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conexion' in locals() and conexion.is_connected():
            conexion.close()

# Función para obtener datos de Excel
def obtener_datos_excel():
    try:
        df_excel = pd.read_excel(ruta_excel, usecols=["linea", "nestacion", "codigo_asc", "nombre"], engine="openpyxl")
        for col in ["linea", "nestacion", "codigo_asc", "nombre"]:
            df_excel[col] = df_excel[col].astype(str).str.strip().str.upper()
        return df_excel
    except FileNotFoundError as err:
        print(f"Error al leer el archivo Excel: {err}")
        return pd.DataFrame()

# Función para unir los DataFrames
def unir_dataframes(df_sql, df_excel):
    if df_sql.empty or df_excel.empty:
        return pd.DataFrame()
    df_sql["linea"] = df_sql["linea"].astype(str).str.strip().str.upper()
    df_sql["nestacion"] = df_sql["nestacion"].astype(str).str.upper()
    df_sql["codigo_asc"] = df_sql["codigo_asc"].astype(str).str.upper()
    df_merged = df_excel.merge(df_sql[["nestacion", "linea", "codigo_asc", "Estado", "fecha_inicial", "fecha_final", "observaciones"]],
                                     on=["nestacion", "linea", "codigo_asc"], how="left")
    df_merged["Estado"] = df_merged["Estado"].fillna("Operativo")
    columnas_renombradas = {
        "linea": "LINEA",
        "nestacion": "ESTACION",
        "codigo_asc": "CÓDIGO ASCENSOR",
        "nombre": "NOMBRE",
        "Estado": "ESTADO",
        "fecha_inicial": "FECHA INICIAL",
        "fecha_final": "FECHA FINAL",
        "observaciones": "Observaciones"
    }
    df_merged.rename(columns=columnas_renombradas, inplace=True)
    return df_merged

# Función para interrupciones
def obtener_datos_interrupciones(fecha_inicio, fecha_fin, tipo_mant):
    try:
        conexion = mysql.connector.connect(host=host, user=user, password=password, database=database)
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT linea, nestacion
            FROM ascensores
            WHERE tipo_mant = %s AND fecha_inicial BETWEEN %s AND %s
        """, (tipo_mant, fecha_inicio, fecha_fin))
        resultados = cursor.fetchall()
        return pd.DataFrame(resultados, columns=["linea", "nestacion"])
    except mysql.connector.Error as err:
        print(f"Error de conexión a MySQL: {err}")
        return pd.DataFrame(columns=["linea", "nestacion"])
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conexion' in locals() and conexion.is_connected(): conexion.close()

# Cargar datos iniciales (se hace fuera del layout)
df_sql_inicial = obtener_datos_mysql()
df_excel_inicial = obtener_datos_excel()
df_merged_inicial = unir_dataframes(df_sql_inicial, df_excel_inicial)

print("Primeras filas de df_merged_inicial:")
print(df_merged_inicial.head())
print("\nColumnas de df_merged_inicial:")
print(df_merged_inicial.columns)

layout = material.PageGrid(
    [
        material.InnerRow(
            [
                material.Span12(
                    [
                        html.H1("Dashboard de Ascensores", className="text-center text-3xl font-bold mb-6 text-gray-800"),
                    ]
                ),
            ]
        ),
        html.Div(className="flex flex-wrap -mx-4", children=[
            html.Div(className="w-full lg:w-1/3 px-4 mb-6", children=[
                material.Span12(children=[
                    html.H3("Estado General de Ascensores", className="text-xl font-semibold mb-2 text-blue-600"),
                    dcc.Graph(id="grafico-general")
                ])
            ]),
            html.Div(className="w-full lg:w-2/3 px-4 mb-6", children=[
                material.Span12(children=[
                    html.H3("Tabla de Estados de Ascensores", className="text-xl font-semibold mb-2 text-green-600"),
                    dash_table.DataTable(
                        id='tabla-ascensores',
                        columns=[{"name": i, "id": i} for i in df_merged_inicial.columns],
                        data=df_merged_inicial.to_dict('records'),
                        page_size=10,
                        filter_action='native',
                        style_table={'overflowX': 'auto', 'minWidth': '100%'},
                        style_cell={'minWidth': '120px', 'maxWidth': '250px', 'whiteSpace': 'normal',
                                    'textAlign': 'left', 'fontFamily': 'Arial Narrow', 'fontSize': '14px'},
                        style_header={'backgroundColor': '#333333', 'fontWeight': 'bold', 'fontFamily': 'Arial Narrow', 'fontSize': '15px', 'color': '#ffffff'},
                        style_data_conditional=[
                            {'if': {'filter_query': '{ESTADO} = "Inoperativo"'}, 'backgroundColor': '#EF4444', 'color': 'white'}
                        ]
                    )
                ])
            ]),
        ]),
        html.Div(className="flex flex-wrap -mx-4 mb-6", children=[
            html.Div(className="w-full lg:w-1/2 px-4", children=[
                material.Span12(children=[
                    html.Label("Selecciona una Línea", className="block mb-2 text-gray-700 font-semibold"),
                    dcc.Dropdown(
                        id="filtro-linea",
                        options=[{"label": linea, "value": linea} for linea in df_merged_inicial["LINEA"].unique()],
                        value=df_merged_inicial["LINEA"].unique()[0] if not df_merged_inicial.empty else None,
                        clearable=False,
                        className="shadow-md rounded-md w-full"
                    ),
                    html.Div(id="tabla-filtrada-container", className="mt-4", children=[ # Contenedor para la tabla filtrada
                        dash_table.DataTable(
                            id='tabla-filtrada-data', # Mismo ID que antes, ahora renderizado aquí
                            columns=[],
                            data=[],
                            page_size=10,
                            filter_action='native',
                            style_table={'overflowX': 'auto', 'minWidth': '100%'},
                            style_cell={'minWidth': '120px', 'maxWidth': '250px', 'whiteSpace': 'normal',
                                        'textAlign': 'left', 'fontFamily': 'Arial Narrow', 'fontSize': '14px'},
                            style_header={'backgroundColor': '#333333', 'fontWeight': 'bold', 'fontFamily': 'Arial Narrow', 'fontSize': '15px', 'color': '#ffffff'},
                            style_data_conditional=[
                                {'if': {'filter_query': '{ESTADO} = "Inoperativo"'}, 'backgroundColor': '#EF4444', 'color': 'white'}
                            ]
                        )
                    ])
                ])
            ]),
            html.Div(className="w-full lg:w-1/2 px-4", children=[
                material.Span12(children=[
                    html.H3("Estados por Línea", className="text-xl font-semibold mb-2 text-purple-600"),
                    dcc.Graph(id="grafico-estados")
                ])
            ]),
        ]),
        html.Div(className="bg-gray-100 p-4 rounded-md shadow-md", children=[
            material.Span12(
                [
                    html.H2("Tipos de Mantenimiento por Líneas", className="text-xl font-semibold text-center mb-4 text-indigo-700"),
                    html.Div(className="flex justify-center space-x-4 mb-4", children=[
                        dcc.DatePickerRange(
                            id="fecha-selector",
                            start_date=date(2020, 1, 1),
                            end_date=date(2025, 12, 31),
                            display_format='DD-MM-YYYY',
                            className="shadow-md rounded-md"
                        ),
                        dcc.Dropdown(
                            id="tipo-mant-selector",
                            options=[
                                {"label": "Interrupción", "value": "interrupcion"},
                                {"label": "Correctivo", "value": "correctivo"},
                                {"label": "Preventivo", "value": "preventivo"}
                            ],
                            value="interrupcion",
                            clearable=False,
                            className="w-48 shadow-md rounded-md"
                        )
                    ]),
                    dcc.Graph(id="grafico-interrupciones"),
                    html.Div(id="tabla-interrupciones", className="mt-4", children=[ # Contenedor para la tabla de interrupciones
                        dash_table.DataTable(
                            id='tabla-interrupciones-data',
                            columns=[{"name": "Línea", "id": "linea"}, {"name": "Estación", "id": "nestacion"}],
                            data=[],
                            page_size=10,
                            style_table={'overflowX': 'auto', 'minWidth': '100%'},
                            style_cell={'minWidth': '100px', 'textAlign': 'left', 'fontFamily': 'Arial Narrow', 'fontSize': '14px'},
                            style_header={'backgroundColor': '#333333', 'fontWeight': 'bold', 'fontFamily': 'Arial Narrow', 'fontSize': '15px', 'color': '#ffffff'}
                        )
                    ])
                ]
            )
        ])

    ]
)
dashboard = Dashboard(
    app_name="ascensores",
    title="Ascensores",
    icon="elevator",
    layout=layout,
    # external_stylesheets ya no es necesario aquí, se usa la carpeta assets
)

@dashboard.callback(
    [Output("grafico-estados", "figure"),
     Output("grafico-general", "figure"),
     Output("tabla-filtrada-data", "columns"), # Actualizar las columnas de la tabla
     Output("tabla-filtrada-data", "data")],   # Actualizar los datos de la tabla
    [Input("filtro-linea", "value")]
)
def actualizar_graficos_y_tabla(linea):
    df = df_merged_inicial[df_merged_inicial["LINEA"] == linea] if linea else df_merged_inicial
    df = df.copy()
    df["FECHA INICIAL"] = df["FECHA INICIAL"].astype(str)
    df["FECHA FINAL"] = df["FECHA FINAL"].astype(str)
    print("Valores únicos de ESTADO en df:")
    print(df['ESTADO'].unique())
    print("\nValores únicos de ESTACION en df:")
    print(df['ESTACION'].unique())

    conteo = df.groupby(["ESTADO", "ESTACION"]).size().reset_index(name="Cantidad")

    # Limpiar y estandarizar la columna ESTADO
    conteo["ESTADO"] = conteo["ESTADO"].fillna("Desconocido").astype(str).str.strip().str.capitalize()
    #conteo["ESTADO"] = conteo["ESTADO"].astype(str).str.strip().str.capitalize()
    print("\nValores únicos de ESTADO en conteo (después de limpieza):")
    print(conteo['ESTADO'].unique())

    if conteo.empty:
        fig1 = px.bar(title="No hay datos para esta línea seleccionada")
    else:
        fig1 = px.bar(conteo, x="ESTACION", y="Cantidad", color="ESTADO",
                      color_discrete_map={'Operativo': 'green', 'Inoperativo': 'red'}, text="Cantidad")
        fig1.update_traces(textposition='inside', textfont_size=14)

    total = df_merged_inicial["ESTADO"].value_counts()
    fig2 = px.pie(values=total.values, names=total.index,
                  color=total.index, color_discrete_map={'Operativo': 'green', 'Inoperativo': 'red'})

    columns = [{"name": i, "id": i} for i in df.columns]
    data = df.applymap(lambda x: x.item() if hasattr(x, "item") else x).to_dict("records")

    return fig1, fig2, columns, data

@dashboard.callback(
    Output("grafico-interrupciones", "figure"),
    Output("tabla-interrupciones", "children"),
    [Input("fecha-selector", "start_date"),
     Input("fecha-selector", "end_date"),
     Input("tipo-mant-selector", "value")]
)
def actualizar_grafico_interrupciones(fecha_inicio, fecha_fin, tipo_mant):
    df = obtener_datos_interrupciones(fecha_inicio, fecha_fin, tipo_mant)
    if df.empty:
        return px.bar(title="No hay datos disponibles"), html.Div("No hay datos disponibles para el filtro seleccionado.")

    df_grouped = df.groupby(["linea", "nestacion"]).size().reset_index(name="count")
    fig = px.bar(df_grouped, x="linea", y="count", color="nestacion",
                    title=f"Tipo de Mantenimiento - {tipo_mant.capitalize()} ({fecha_inicio} - {fecha_fin})",
                    text="count")
    fig.update_traces(textposition='outside')
    fig.update_layout(title_x=0.5)

    tabla_interrupciones = dash_table.DataTable(
        id='tabla-interrupciones-data',
        columns=[{"name": "Línea", "id": "linea"}, {"name": "Estación", "id": "nestacion"}],
        #data=df.to_dict('records'),
        data=df.applymap(lambda x: x.item() if hasattr(x, "item") else x).to_dict('records'),
        page_size=10,
        style_table={'overflowX': 'auto', 'minWidth': '100%'},
        style_cell={'minWidth': '100px', 'textAlign': 'left', 'fontFamily': 'Arial Narrow', 'fontSize': '14px'},
        style_header={'backgroundColor': '#333333', 'fontWeight': 'bold', 'fontFamily': 'Arial Narrow', 'fontSize': '15px', 'color': '#ffffff'}
    )

    return fig, tabla_interrupciones

if __name__ == "__main__":
    dashboard.run()