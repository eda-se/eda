from io import StringIO

from dash import dcc, html, callback, Input, Output, State
from dash.exceptions import PreventUpdate
import pandas as pd
import plotly.express as px


def register_graph_callbacks():
    @callback(
        Output('graph_output', 'children', allow_duplicate=True),
        Input('dataframe', 'data'),
        prevent_initial_call=True
    )
    def render(df_json: str):
        df = pd.read_json(StringIO(df_json))

        return html.Div([
            html.H1("Generacja grafu", style={'fontSize': '36px'}),
            html.Div(id='dropdowns_2d'),
            html.Div(id='current_chosen'),
            html.Div([
                html.Label("Wybierz zakres wierszy:"),
                dcc.Input(id='start-row', type='number', placeholder='Początkowy wiersz', min=0, max=len(df) - 1,
                          value=0),
                dcc.Input(id='end-row', type='number', placeholder='Końcowy wiersz', min=0, max=len(df) - 1,
                          value=len(df) - 1),
            ]),
            html.Button('Wygeneruj wykres liniowy', id='generate_line_graph', n_clicks=0),

            dcc.Graph(id='line-chart'),

        ])

    @callback(
        Output('dropdowns_2d', 'children'),
        Input('data-table', 'data'),
        prevent_initial_call=True
    )
    def update_dropdowns(data_table):
        df = pd.DataFrame(data_table)
        options = [{'label': col, 'value': col} for col in df.columns]
        dropdowns = html.Div([
            html.Label(f'Wybierz kolumnę x: '),
            dcc.Dropdown(options=options, id='x-axis-dropdown'),
            html.Label(f'Wybierz kolumnę y: '),
            dcc.Dropdown(options=options, id='y-axis-dropdown')
        ])

        return dropdowns


    @callback(
        Output('current_chosen', 'children'),
        Output('line-chart', 'figure'),
        Input('generate_line_graph', 'n_clicks'),
        State('stored-dataframe', 'data'),
        State('x-axis-dropdown', 'value'),
        State('y-axis-dropdown', 'value'),
        State('start-row', 'value'),
        State('end-row', 'value'),
        prevent_initial_call=True
    )
    def generate_line_graph(n_clicks, data_table, x_col, y_col, start_row, end_row):
        if data_table is None or x_col is None or y_col is None:
            raise PreventUpdate

        info = f"Aktualnie wybrane wartości: {x_col}, {y_col}, Wiersze: {start_row}-{end_row}"

        #df = pd.DataFrame(data_table)
        df = pd.read_json(StringIO(data_table))
        filtered_df = df.iloc[start_row:end_row + 1]

        fig = px.line(filtered_df, x=x_col, y=y_col)
        return info, fig



