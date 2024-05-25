from io import StringIO

from dash import dcc, html, callback, Input, Output, State, dash_table, no_update
from dash.exceptions import PreventUpdate
from eda.destats import *


def register_1d_stats_callbacks():
    @callback(
        Output('statistic_output', 'children', allow_duplicate=True),
        Input('dataframe', 'data'),
        prevent_initial_call=True
    )
    def render(df_json: str):
        df = pd.read_json(StringIO(df_json))

        return html.Div(id="stats-1d", children=[
            html.H2("Statystki opisowe 1D"),
            html.Div(id='stats-1d__dropdown'),
            html.Div(id='stats-1d__selected-variable'),
            html.Div(id='stats-1d__summary'),
            html.Div(id='stats-1d__details', style={'width': '30%', 'display': 'inline-block'}),
        ])

    @callback(
        Output('stats-1d__dropdown', 'children'),
        Input('data-table', 'data'),
        prevent_initial_call=True
    )
    def update_dropdowns(data_table):
        df = pd.DataFrame(data_table)
        options = [{'label': col, 'value': col} for col in df.columns]
        dropdown = html.Div([
            html.Label(f'Wybierz kolumnę, dla której chcesz obliczyć statystyki: '),
            dcc.Dropdown(options=options, id='1d-dropdown')
        ])

        return dropdown

    @callback(
        Output('stats-1d__selected-variable', 'children'),
        Output('stats-1d__summary', 'children'),
        Input('1d-dropdown', 'value'),
        State('data-table', 'data'),
        State('stored-dtypes', 'data'),
        prevent_initial_call=True
    )
    def computing_stats(col, data, dtypes):
        if col is None:
            raise PreventUpdate

        info = f"Aktualnie wybrana wartość: {col}"
        df = pd.DataFrame(data)
        values = df[col]

        if dtypes[col] == 'int64' or dtypes[col] == 'float64':
            return info, numeric_stats(values)
        else:
            return info, categorical_stats(values)

    def numeric_stats(values):
        labels = [
            "Liczba pustych wartości",
            "Mediana",
            "Średnia",
            "Odchylenie standardowe",
            "Wariancja",
            "Rozstęp",
            "Skośność/asymetria rozkładu"
        ]
        functions = [
            na_count_1d(values),
            median_1d(values),
            mean_1d(values),
            std_deviation_1d(values),
            variance_1d(values),
            range_1d(values),
            skewness_1d(values)
        ]
        quantile_values = quantiles_1d(values, [0.25, 0.5, 0.75])

        stats = [
            html.Div([
                html.H3(label + ":"),
                html.Pre(function)
            ])
            for label, function in zip(labels, functions)
        ]
        stats += [
            html.Div([
                html.H3("Kwantyle"),
                html.P(className="stats__paragraph", children=[
                    "¼",
                    html.Pre(quantile_values[0.25], className="stats__value"),
                ]),
                html.P(className="stats__paragraph", children=[
                    "½",
                    html.Pre(quantile_values[0.5], className="stats__value"),
                ]),
                html.P(className="stats__paragraph", children=[
                    "¾",
                    html.Pre(quantile_values[0.75], className="stats__value"),
                ]),
            ])
        ]

        return stats

    def categorical_stats(values):
        labels = [
            "Liczba wartości brakujących",
        ]
        functions = [
            na_count_1d(values),
        ]

        stats = [
            html.Div([
                html.H3(label + ":"),
                html.Pre(function)
            ])
            for label, function in zip(labels, functions)
        ]

        return stats

    @callback(
        Output('stats-1d__details', 'children'),
        Input('1d-dropdown', 'value'),
        State('data-table', 'data'),
        State('stored-dtypes', 'data'),
        prevent_initial_call=True
    )
    def generate_tables(col, data, dtypes):
        if data is None or col is None:
            raise PreventUpdate

        df = pd.DataFrame(data)
        values = df[col]

        if dtypes[col] == 'int64' or dtypes[col] == 'float64':
            return numeric_tables(values)
        return categorical_tables(values)

    def numeric_tables(values):
        mode_values = mode_1d(values)
        mode_occurrences = values[values == mode_values[0]].count()
        mode_paragraph_content = "Liczba wystąpień poniższej wartości: "
        if mode_values.size > 1:
            mode_paragraph_content = "Liczba wystąpień poniższej wartości: "
        mode_paragraph_content += f"{mode_occurrences}."

        return [
            html.Div([
                html.H4("Moda"),
                html.P(mode_paragraph_content),
                dash_table.DataTable(
                    data=[
                        {"value": value}
                        for value in mode_values
                    ],
                    columns=[
                        {"name": 'Wartość zmiennej', "id": "value"},
                    ]
                )
            ])
        ]

    def categorical_tables(values):
        unique_values = np.sort(unique_1d(values))
        count_values = count_1d(values).sort_values(ascending=False)
        proportion_values = proportion_1d(values).sort_values(ascending=False)

        return [
            html.Div([
                html.H4("Unikalne wartości"),
                dash_table.DataTable(
                    data=[
                        {"Unikalne wartości": v}
                        for v in unique_values
                    ],
                    columns=[
                        {"name": "Unikalne wartości", "id": "Unikalne wartości"}
                    ],
                    page_size=10
                )
            ]),
            html.Div([
                html.H4("Liczność"),
                dash_table.DataTable(
                    data=[
                        {"Wartość": key, "Liczebność": value}
                        for key, value in count_values.items()
                    ],
                    columns=[
                        {"name": "Wartość", "id": "Wartość"},
                        {"name": "Liczebność", "id": "Liczebność"}
                    ],
                    page_size=10
                )
            ]),
            html.Div([
                html.H4("Proporcja"),
                dash_table.DataTable(
                    data=[
                        {"Wartość": key, "Proporcja": value}
                        for key, value in proportion_values.items()
                    ],
                    columns=[
                        {"name": "Wartość", "id": "Wartość"},
                        {"name": "Proporcja", "id": "Proporcja"}
                    ],
                    page_size=10
                )
            ]),
        ]
