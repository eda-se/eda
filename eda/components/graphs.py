from io import StringIO

from dash import dcc, html, callback, Input, Output, State
from dash.exceptions import PreventUpdate
import pandas as pd
import plotly.express as px

from eda.data_table.column_type import is_number_type, is_categorical_type


def register_graph_callbacks():
    @callback(
        Output('graph_output', 'children', allow_duplicate=True),
        Input('dataframe', 'data'),
        prevent_initial_call=True
    )
    def render(df_json: str):
        df = pd.read_json(StringIO(df_json))

        return html.Div([
            html.H2("Wizualizacja danych"),
            html.Div(id='dropdowns_2d'),
            html.Div([
                html.Label("Wybierz zakres wierszy:"),
                dcc.Input(id='start-row', type='number', placeholder='Początkowy wiersz', min=0, max=len(df) - 1,
                          value=0),
                dcc.Input(id='end-row', type='number', placeholder='Końcowy wiersz', min=0, max=len(df) - 1,
                          value=len(df) - 1),
            ]),
            html.Div(id='current_chosen'),
            html.Div(id='stats-2d__buttons'),
            html.Div(id='stats-2d__chart'),
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
        Output('stats-2d__buttons', 'children'),
        Output('stats-2d__chart', 'children', allow_duplicate=True),
        Input('x-axis-dropdown', 'value'),
        Input('y-axis-dropdown', 'value'),
        State('stored-dtypes', 'data'),
        prevent_initial_call=True
    )
    def generate_buttons(x, y, dtypes):
        if x is None or y is None:
            raise PreventUpdate

        buttons = [
            html.Button('liniowy', id="2d-line-chart"),
            html.Button('punktowy', id="2d-scatter-chart"),
            html.Button('mapa ciepła', id="2d-heatmap-chart")
        ]

        if is_categorical_type(dtypes[x]):
            if is_categorical_type(dtypes[y]):
                buttons = [
                    html.Button('słupkowy', id="2d-bar-chart"),
                    html.Button('mapa ciepła', id="2d-heatmap-chart")
                ]
            else:
                if is_number_type(dtypes[y]):
                    buttons = [
                        html.Button('punktowy', id="2d-scatter-chart"),
                        html.Button('pudelkowy', id="2d-box-chart")
                    ]
        if is_number_type(dtypes[x]):
            buttons.append(html.Button('punktowy z linią trendu', id="2d-trend-chart"))

        return ["wygeneruj wykres: "] + buttons, None



    @callback(
        Output('current_chosen', 'children', allow_duplicate=True),
        Output('stats-2d__chart', 'children', allow_duplicate=True),
        Input('2d-line-chart', 'n_clicks'),
        State('data-table', 'data'),
        State('x-axis-dropdown', 'value'),
        State('y-axis-dropdown', 'value'),
        State('start-row', 'value'),
        State('end-row', 'value'),
        prevent_initial_call=True
    )
    def generate_line_graph(n_clicks, data_table, x_col, y_col, start_row, end_row):
        if data_table is None or x_col is None or y_col is None:
            raise PreventUpdate

        info = f"Aktualnie wybrane wartości: x={x_col}, y={y_col}, Wiersze: {start_row}-{end_row}"

        df = pd.DataFrame(data_table)
        filtered_df = df.iloc[start_row:end_row + 1]

        fig = px.line(filtered_df, x=x_col, y=y_col)
        return info, dcc.Graph(figure=fig)

    @callback(
        Output('current_chosen', 'children', allow_duplicate=True),
        Output('stats-2d__chart', 'children', allow_duplicate=True),
        Input('2d-trend-chart', 'n_clicks'),
        State('data-table', 'data'),
        State('x-axis-dropdown', 'value'),
        State('y-axis-dropdown', 'value'),
        State('start-row', 'value'),
        State('end-row', 'value'),
        prevent_initial_call=True
    )
    def generate_scatter_graph_with_trend(n_clicks, data_table, x_col, y_col, start_row, end_row):
        if data_table is None or x_col is None or y_col is None:
            raise PreventUpdate

        info = f"Aktualnie wybrane wartości: x={x_col}, y={y_col}, Wiersze: {start_row}-{end_row}"

        df = pd.DataFrame(data_table)
        filtered_df = df.iloc[start_row:end_row + 1]

        fig = px.scatter(filtered_df, x=x_col, y=y_col, trendline="ols")
        fig.update_traces(selector=dict(name="trendline"), line=dict(color='green'))  # Zmiana koloru linii trendu

        return info, dcc.Graph(figure=fig)

    @callback(
        Output('current_chosen', 'children', allow_duplicate=True),
        Output('stats-2d__chart', 'children', allow_duplicate=True),
        Input('2d-heatmap-chart', 'n_clicks'),
        State('data-table', 'data'),
        State('x-axis-dropdown', 'value'),
        State('y-axis-dropdown', 'value'),
        State('start-row', 'value'),
        State('end-row', 'value'),
        prevent_initial_call=True
    )
    def heatmap_chart(n_clicks, data, column1, column2, start_row, end_row):
        if n_clicks is None or column1 is None or column2 is None or data is None:
            raise PreventUpdate

        info = f"Aktualnie wybrane wartości: x={column1}, y={column2}, Wiersze: {start_row}-{end_row}"

        df = pd.DataFrame(data)
        selected_rows = df.iloc[start_row:end_row + 1]

        selected_rows = selected_rows.groupby([column1, column2]).mean().reset_index()

        fig = px.imshow(selected_rows.pivot(index=column1, columns=column2, values='Wartość'),
                        labels=dict(x=column2, y=column1, color="Wartość"),
                        title="Heatmapa")

        return info, dcc.Graph(figure=fig)

    @callback(
        Output('current_chosen', 'children', allow_duplicate=True),
        Output('stats-2d__chart', 'children', allow_duplicate=True),
        Input('2d-box-chart', 'n_clicks'),
        State('data-table', 'data'),
        State('x-axis-dropdown', 'value'),
        State('y-axis-dropdown', 'value'),
        State('start-row', 'value'),
        State('end-row', 'value'),
        prevent_initial_call=True
    )
    def generate_box_plot(n_clicks, data, column1, column2, start_row, end_row):
        if n_clicks is None or column1 is None or column2 is None or data is None:
            raise PreventUpdate

        info = f"Aktualnie wybrane wartości: x={column1}, y={column2}, Wiersze: {start_row}-{end_row}"

        df = pd.DataFrame(data)
        selected_rows = df.iloc[start_row:end_row + 1]

        fig_box = px.box(selected_rows, x=column1, y=column2, title="Wykres pudelkowy")

        return info, dcc.Graph(figure=fig_box)

    @callback(
        Output('current_chosen', 'children', allow_duplicate=True),
        Output('stats-2d__chart', 'children', allow_duplicate=True),
        Input('2d-scatter-chart', 'n_clicks'),
        State('data-table', 'data'),
        State('x-axis-dropdown', 'value'),
        State('y-axis-dropdown', 'value'),
        State('start-row', 'value'),
        State('end-row', 'value'),
        prevent_initial_call=True
    )
    def generate_scatter_plot(n_clicks, data, column1, column2, start_row, end_row):
        if n_clicks is None or column1 is None or column2 is None or data is None:
            raise PreventUpdate

        info = f"Aktualnie wybrane wartości: x={column1}, y={column2}, Wiersze: {start_row}-{end_row}"

        df = pd.DataFrame(data)
        selected_rows = df.iloc[start_row:end_row + 1]

        fig_scatter = px.scatter(selected_rows, x=column1, y=column2, title="Wykres punktowy")

        return info, dcc.Graph(figure=fig_scatter)

    @callback(
        Output('current_chosen', 'children', allow_duplicate=True),
        Output('stats-2d__chart', 'children', allow_duplicate=True),
        Input('2d-bar-chart', 'n_clicks'),
        State('data-table', 'data'),
        State('x-axis-dropdown', 'value'),
        State('y-axis-dropdown', 'value'),
        State('start-row', 'value'),
        State('end-row', 'value'),
        prevent_initial_call=True
    )
    def generate_bar_plot(n_clicks, data, column1, column2, start_row, end_row):
        if n_clicks is None or column1 is None or column2 is None or data is None:
            raise PreventUpdate

        info = f"Aktualnie wybrane wartości: x={column1}, y={column2}, Wiersze: {start_row}-{end_row}"

        df = pd.DataFrame(data)
        selected_rows = df.iloc[start_row:end_row + 1]

        selected_rows[column1] = selected_rows[column1].astype(str)
        selected_rows[column2] = selected_rows[column2].astype(str)

        grouped_data = selected_rows.groupby([column1, column2]).size().reset_index()
        grouped_data.columns = [column1, column2, 'Count']

        fig_bar = px.bar(grouped_data, x=column1, y='Count', color=column2,
                         title=f'Wykres słupkowy dla {column1} z podziałem na {column2}')

        return info, dcc.Graph(figure=fig_bar)


