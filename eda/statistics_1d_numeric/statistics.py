from io import StringIO

from dash import dcc, html, callback, Input, Output, State, dash_table
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
            html.Div(id='tables-container', style={'width': '30%', 'display': 'inline-block'}),

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
        State('data-table', 'data'),
        State('stored-dtypes', 'data'),
        prevent_initial_call=True
    )
    def computing_stats(col, data, dtypes):
        if col is None:
            raise PreventUpdate
        if dtypes[col] != 'int64' and dtypes[col] != 'float64':
            raise PreventUpdate
        info = f"Aktualnie wybrana wartość: {col}"
        df = pd.DataFrame(data)
        values = df[col]

        labels = ["Liczba pustycz wartości:", "Mediana:", "Średnia:", "Odchylenie standardowe:", "Wariancja:", "Rozstęp:", "Skośność/asymetria rozkładu:"]
        functions = [na_count_1d(values), median_1d(values), mean_1d(values), std_deviation_1d(values), variance_1d(values), range_1d(values), skewness_1d(values)]

        stats = []
        for label, func in zip(labels, functions):
            stats.append(
                html.Div([
                    html.H3(label),
                    html.Pre(func)
                ]),
            )
        return info, stats

    @callback(
        Output('tables-container', 'children'),
        Input('1d-dropdown', 'value'),
        State('data-table', 'data'),
        State('stored-dtypes', 'data'),
        prevent_initial_call=True
    )
    def generate_tables(col, data, dtypes):
        if data is None or col is None:
            raise PreventUpdate
        if dtypes[col] != 'int64' and dtypes[col] != 'float64':
            raise PreventUpdate

        df = pd.DataFrame(data)
        values = df[col]

        unique_values = np.sort(unique_1d(values))
        count_values = count_1d(values).sort_values(ascending=False)
        proportion_values = proportion_1d(values).sort_values(ascending=False)
        mode_values = mode_1d(values)
        quantiles_values = quantiles_1d(values, [0.25, 0.5, 0.75])

        tables = [html.Div([
            html.H4('Unikalne wartości'),
            dash_table.DataTable(
                data=[{'Unikalne wartości': v} for v in unique_values],
                columns=[{'name': 'Unikalne wartości', 'id': 'Unikalne wartości'}],
                page_size=10
            )
        ]), html.Div([
            html.H4('Liczebność wartości'),
            dash_table.DataTable(
                data=[{'Wartość': key, 'Liczebność': value} for key, value in count_values.items()],
                columns=[{'name': 'Wartość', 'id': 'Wartość'}, {'name': 'Liczebność', 'id': 'Liczebność'}],
                page_size=10
            )
        ]), html.Div([
            html.H4('Proporcje wartości'),
            dash_table.DataTable(
                data=[{'Wartość': key, 'Proporcja': value} for key, value in proportion_values.items()],
                columns=[{'name': 'Wartość', 'id': 'Wartość'}, {'name': 'Proporcja', 'id': 'Proporcja'}],
                page_size=10
            )
        ]), html.Div([
            html.H4('Kwantyle'),
            dash_table.DataTable(
                data=[{'index': key, 'val': value} for key, value in quantiles_values.items()],
                columns=[{'name': 'Kwantyl', 'id': 'index'}, {'name': 'Wartość kwantylu', 'id': 'val'}]
            )
        ])]

        return tables


