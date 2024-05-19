from io import StringIO

from dash import dcc, html, callback, Input, Output, State
from dash.exceptions import PreventUpdate
from eda.statistics_1d_numeric.destats import *


def register_1d_stats_callbacks():
    @callback(
        Output('statistic_output', 'children', allow_duplicate=True),
        Input('dataframe', 'data'),
        prevent_initial_call=True
    )
    def render(df_json: str):
        df = pd.read_json(StringIO(df_json))

        return html.Div([
            html.H1("Statystki 1D", style={'fontSize': '36px'}),
            html.Div(id='dropdown_1d'),
            html.Div(id='show_current_1d_val'),
            html.Div(id='stats-container'),

        ])

    @callback(
        Output('dropdown_1d', 'children'),
        Input('data-table', 'data'),
        prevent_initial_call=True
    )
    def update_dropdowns(data_table):
        df = pd.DataFrame(data_table)
        options = [{'label': col, 'value': col} for col in df.columns]
        dropdown = html.Div([
            html.Label(f'Wybierz kolumnę, której statystyki chcesz obliczyć: '),
            dcc.Dropdown(options=options, id='1d-dropdown')
        ])

        return dropdown

    @callback(
        Output('show_current_1d_val', 'children'),
        Output('stats-container', 'children'),
        Input('1d-dropdown', 'value'),
        State('stored-dataframe', 'data'),
        State('stored-dtypes', 'data'),
        prevent_initial_call=True
    )
    def computing_stats(col, data, dtypes):
        if col is None:
            raise PreventUpdate
        if dtypes[col] != 'int64' and dtypes[col] != 'float64':
            raise PreventUpdate
        info = f"Aktualnie wybrana wartość: {col}"
        df = pd.read_json(StringIO(data))
        values = df[col]
        stats = [
            html.Div([
                html.H3("Mode:"),
                html.Pre(mode_1d(values))
            ]),
            html.Div([
                html.H3("NA count:"),
                html.Pre(na_count_1d(values))
            ]),
            html.Div([
                html.H3("Median:"),
                html.Pre(median_1d(values))
            ]),
            html.Div([
                html.H3("Mean:"),
                html.Pre(mean_1d(values))
            ]),
            html.Div([
                html.H3("Standard deviation:"),
                html.Pre(std_deviation_1d(values))
            ]),
            html.Div([
                html.H3("Variance:"),
                html.Pre(variance_1d(values))
            ]),
            html.Div([
                html.H3("Quantiles:"),
                html.Pre(quantiles_1d(values, [0.25, 0.5, 0.75]))
            ]),
            html.Div([
                html.H3("Range:"),
                html.Pre(range_1d(values))
            ]),
            html.Div([
                html.H3("Skewness:"),
                html.Pre(skewness_1d(values))
            ])
        ]
        return info, stats


