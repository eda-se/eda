from dash import dcc, html, callback, Input, Output, State
from dash.exceptions import PreventUpdate
import pandas as pd
import plotly.express as px

from eda.data_table.column_type import is_number_type, is_categorical_type, is_data_type


def register_graph_callbacks():
    @callback(
        Output('stats-2d__charts', 'children'),
        Output('stats-2d__reverse', 'children', allow_duplicate=True),
        Input('2d-dropdown1', 'value'),
        Input('2d-dropdown2', 'value'),
        Input('stats-2d__reverse', 'n_clicks'),
        State('stored-dtypes', 'data'),
        State('data-table', 'data'),
        Input('start-row', 'value'),
        Input('end-row', 'value'),
        prevent_initial_call=True
    )
    def generate_charts(x, y, clicks, dtypes, df, start_row, end_row):
        if x is None or y is None:
            raise PreventUpdate
        data = pd.DataFrame(df)

        charts = [
            generate_scatter_plot(clicks, data, x, y, start_row, end_row),
            heatmap_chart(clicks, data, x, y, start_row, end_row),
        ]
        if is_data_type(dtypes[x]):
            charts.extend([
                generate_line_graph(data, x, y, start_row, end_row)
            ])
        if is_categorical_type(dtypes[x]):
            if is_categorical_type(dtypes[y]):
                charts = [
                    generate_bar_plot(clicks, data, x, y, start_row, end_row),
                    heatmap_chart(clicks, data, x, y, start_row, end_row),
                ]
            else:
                if is_number_type(dtypes[y]):
                    charts = [
                        generate_scatter_plot(clicks, data, x, y, start_row, end_row),
                        generate_box_plot(data, x, y, start_row, end_row)
                    ]
        if is_number_type(dtypes[x]) and is_number_type(dtypes[y]):
            charts = [
                generate_scatter_graph_with_trend(clicks, data, x, y, start_row, end_row),
                heatmap_chart(clicks, data, x, y, start_row, end_row),
            ]
        return charts, html.Button('zamień', id="reverse"),

    def generate_line_graph(data_table, x_col, y_col, start_row, end_row):
        if data_table is None or x_col is None or y_col is None:
            raise PreventUpdate

        df = pd.DataFrame(data_table)
        filtered_df = df.iloc[start_row:end_row + 1]

        fig = px.line(filtered_df, x=x_col, y=y_col)
        return dcc.Graph(figure=fig)

    def generate_scatter_graph_with_trend(clicks, data_table, x_col, y_col, start_row, end_row):
        if data_table is None or x_col is None or y_col is None:
            raise PreventUpdate
        if clicks is not None:
            if clicks % 2 == 1:
                y_col, x_col = x_col, y_col

        df = pd.DataFrame(data_table)
        filtered_df = df.iloc[start_row:end_row + 1]

        fig = px.scatter(filtered_df, x=x_col, y=y_col, trendline="ols",
                         title="Wykres punktowy z linią trendu")
        fig.update_traces(selector=dict(name="trendline"), line=dict(color='green'))  # Zmiana koloru linii trendu

        return dcc.Graph(figure=fig)

    def heatmap_chart(clicks, data, column1, column2, start_row, end_row):
        if column1 is None or column2 is None or data is None:
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

    def generate_box_plot(data, column1, column2, start_row, end_row):
        if column1 is None or column2 is None or data is None:
            raise PreventUpdate

        df = pd.DataFrame(data)
        selected_rows = df.iloc[start_row:end_row + 1]

        fig_box = px.box(selected_rows, x=column1, y=column2, title="Wykres pudelkowy")

        return dcc.Graph(figure=fig_box)

    def generate_scatter_plot(clicks, data, column1, column2, start_row, end_row):
        if column1 is None or column2 is None or data is None:
            raise PreventUpdate

        df = pd.DataFrame(data)
        selected_rows = df.iloc[start_row:end_row + 1]
        if clicks is not None:
            if clicks % 2 == 1:
                column1, column2 = column2, column1

        fig_scatter = px.scatter(selected_rows, x=column1, y=column2, title="Wykres punktowy")

        return dcc.Graph(figure=fig_scatter)

    def generate_bar_plot(clicks, data, column1, column2, start_row, end_row):
        if column1 is None or column2 is None or data is None:
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
