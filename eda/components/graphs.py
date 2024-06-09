from dash import dcc, html, callback, Input, Output, State
from dash.exceptions import PreventUpdate
import pandas as pd
import plotly.express as px

from eda.data_table.column_type import is_number_type, is_categorical_type, is_data_type


def register_graph_callbacks():
    @callback(
        Output('stats-2d__buttons', 'children'),
        Output('stats-2d__chart', 'children', allow_duplicate=True),
        Output('stats-2d__reverse', 'children', allow_duplicate=True),
        Input('2d-dropdown1', 'value'),
        Input('2d-dropdown2', 'value'),
        State('stored-dtypes', 'data'),
        State('data-table', 'data'),
        prevent_initial_call=True
    )
    def generate_buttons(x, y, dtypes, df):
        if x is None or y is None:
            raise PreventUpdate

        chart_range = html.Div([
            html.Label("Wybierz zakres wierszy:"),
            dcc.Input(id='start-row', type='number', placeholder='Początkowy wiersz', min=0, max=len(df) - 1, value=0),
            dcc.Input(id='end-row', type='number', placeholder='Końcowy wiersz', min=0, max=len(df) - 1,
                      value=len(df) - 1)
        ])

        buttons = [
            html.Button('punktowy', id="2d-scatter-chart"),
            html.Button('mapa ciepła', id="2d-heatmap-chart")
        ]
        if is_data_type(dtypes[x]):
            buttons.extend([
                html.Button('liniowy', id="2d-line-chart")
            ])
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
        if is_number_type(dtypes[x]) and is_number_type(dtypes[y]):
            buttons.append(html.Button('punktowy z linią trendu', id="2d-trend-chart"))

        return [html.H3("Wygeneruj wykres: "), chart_range] + buttons, None, html.Button('zamień', id="reverse"),

    @callback(
        Output('stats-2d__chart', 'children', allow_duplicate=True),
        Input('2d-line-chart', 'n_clicks'),
        State('data-table', 'data'),
        State('2d-dropdown1', 'value'),
        State('2d-dropdown2', 'value'),
        State('start-row', 'value'),
        State('end-row', 'value'),
        prevent_initial_call=True
    )
    def generate_line_graph(n_clicks, data_table, x_col, y_col, start_row, end_row):
        if data_table is None or x_col is None or y_col is None:
            raise PreventUpdate

        df = pd.DataFrame(data_table)
        filtered_df = df.iloc[start_row:end_row + 1]

        fig = px.line(filtered_df, x=x_col, y=y_col)
        return dcc.Graph(figure=fig)

    @callback(
        Output('stats-2d__chart', 'children', allow_duplicate=True),
        Input('2d-trend-chart', 'n_clicks'),
        Input('stats-2d__reverse', 'n_clicks'),
        State('data-table', 'data'),
        State('2d-dropdown1', 'value'),
        State('2d-dropdown2', 'value'),
        State('start-row', 'value'),
        State('end-row', 'value'),
        prevent_initial_call=True
    )
    def generate_scatter_graph_with_trend(n_clicks, clicks, data_table, x_col, y_col, start_row, end_row):
        if data_table is None or x_col is None or y_col is None:
            raise PreventUpdate
        if clicks is not None:
            if clicks % 2 == 1:
                y_col, x_col = x_col, y_col

        df = pd.DataFrame(data_table)
        filtered_df = df.iloc[start_row:end_row + 1]

        fig = px.scatter(filtered_df, x=x_col, y=y_col, trendline="ols")
        fig.update_traces(selector=dict(name="trendline"), line=dict(color='green'))  # Zmiana koloru linii trendu

        return dcc.Graph(figure=fig)

    @callback(
        Output('stats-2d__chart', 'children', allow_duplicate=True),
        Input('2d-heatmap-chart', 'n_clicks'),
        Input('stats-2d__reverse', 'n_clicks'),
        State('data-table', 'data'),
        State('2d-dropdown1', 'value'),
        State('2d-dropdown2', 'value'),
        State('start-row', 'value'),
        State('end-row', 'value'),
        prevent_initial_call=True
    )
    def heatmap_chart(n_clicks, clicks, data, column1, column2, start_row, end_row):
        if n_clicks is None or column1 is None or column2 is None or data is None:
            raise PreventUpdate
        if clicks is not None:
            if clicks % 2 == 1:
                column1, column2 = column2, column1

        df = pd.DataFrame(data)
        selected_rows = df.iloc[start_row:end_row + 1]

        fig = px.density_heatmap(selected_rows, x=column1, y=column2, nbinsx=20, nbinsy=20,
                                 labels={column1: column1, column2: column2, 'color': 'Density'},
                                 title="Mapa Gęstości Punktów")

        return dcc.Graph(figure=fig)

    @callback(
        Output('stats-2d__chart', 'children', allow_duplicate=True),
        Input('2d-box-chart', 'n_clicks'),
        State('data-table', 'data'),
        State('2d-dropdown1', 'value'),
        State('2d-dropdown2', 'value'),
        State('start-row', 'value'),
        State('end-row', 'value'),
        prevent_initial_call=True
    )
    def generate_box_plot(n_clicks, data, column1, column2, start_row, end_row):
        if n_clicks is None or column1 is None or column2 is None or data is None:
            raise PreventUpdate

        df = pd.DataFrame(data)
        selected_rows = df.iloc[start_row:end_row + 1]

        fig_box = px.box(selected_rows, x=column1, y=column2, title="Wykres pudelkowy")

        return dcc.Graph(figure=fig_box)

    @callback(
        Output('stats-2d__chart', 'children', allow_duplicate=True),
        Input('2d-scatter-chart', 'n_clicks'),
        Input('stats-2d__reverse', 'n_clicks'),
        State('data-table', 'data'),
        State('2d-dropdown1', 'value'),
        State('2d-dropdown2', 'value'),
        State('start-row', 'value'),
        State('end-row', 'value'),
        prevent_initial_call=True
    )
    def generate_scatter_plot(n_clicks, clicks, data, column1, column2, start_row, end_row):
        if n_clicks is None or column1 is None or column2 is None or data is None:
            raise PreventUpdate

        df = pd.DataFrame(data)
        selected_rows = df.iloc[start_row:end_row + 1]
        if clicks is not None:
            if clicks % 2 == 1:
                column1, column2 = column2, column1

        fig_scatter = px.scatter(selected_rows, x=column1, y=column2, title="Wykres punktowy")

        return dcc.Graph(figure=fig_scatter)

    @callback(
        Output('stats-2d__chart', 'children', allow_duplicate=True),
        Input('2d-bar-chart', 'n_clicks'),
        Input('stats-2d__reverse', 'n_clicks'),
        State('data-table', 'data'),
        State('2d-dropdown1', 'value'),
        State('2d-dropdown2', 'value'),
        State('start-row', 'value'),
        State('end-row', 'value'),
        prevent_initial_call=True
    )
    def generate_bar_plot(n_clicks, clicks, data, column1, column2, start_row, end_row):
        if n_clicks is None or column1 is None or column2 is None or data is None:
            raise PreventUpdate
        if clicks is not None:
            if clicks % 2 == 1:
                column1, column2 = column2, column1

        df = pd.DataFrame(data)
        selected_rows = df.iloc[start_row:end_row + 1]

        selected_rows[column1] = selected_rows[column1].astype(str)
        selected_rows[column2] = selected_rows[column2].astype(str)

        grouped_data = selected_rows.groupby([column1, column2]).size().reset_index()
        grouped_data.columns = [column1, column2, 'Count']

        fig_bar = px.bar(grouped_data, x=column1, y='Count', color=column2,
                         title=f'Wykres słupkowy dla {column1} z podziałem na {column2}')

        return dcc.Graph(figure=fig_bar)
