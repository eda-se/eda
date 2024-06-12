from io import StringIO

from dash import dcc, html, callback, Input, Output, State, dash_table, no_update
from dash.exceptions import PreventUpdate
import dash_ag_grid as dag
import plotly.express as px
from pandas.core.dtypes.common import is_numeric_dtype

from eda.destats import *
from eda.components import H2, H3, H6, P, Button, GridDiv
from eda.data_table.column_type import is_number_type


def register_1d_stats_callbacks():
    MAX_ROWS = 15
    ROW_HEIGHT = 42
    HEADER_ROW_HEIGHT = 49

    @callback(
        Output('statistic_output', 'children', allow_duplicate=True),
        Input('dataframe', 'data'),
        prevent_initial_call=True
    )
    def render(df_json: str):
        return html.Div(id="stats-1d", children=[
            H2("Statystki opisowe 1D"),

            html.Div(id="stats-1d__multiselect"),

            html.Div(id="stats-1d__main", className="py-4 hidden", children=[
                html.Div(className="my-2", children=[
                    GridDiv(id="stats-1d__summary", columns_count=5),
                    html.Div(id="stats-1d__details"),
                ]),

                html.Div(id="stats-1d__charts", className="my-8", children=[
                    H3("Wizualizacja danych"),
                    html.Div(id="stats-1d__charts"),
                ]),
            ])

        ])

    @callback(
        Output('stats-1d__multiselect', 'children'),
        Input('data-table', 'data'),
        prevent_initial_call=True
    )
    def update_dropdowns(data_table):
        df = pd.DataFrame(data_table)
        options = [{'label': col, 'value': col} for col in df.columns]
        dropdown = html.Div([
            H3("Wybór zmiennych"),
            dcc.Dropdown(
                id='multi-select-dropdown',
                options=options,
                multi=True,
                placeholder="Wybierz zmienne"
            ),
        ])

        return dropdown

    @callback(
        Output('stats-1d__summary', 'children'),
        Output('stats-1d__charts', 'children'),
        Output("stats-1d__main", "className"),
        Input('multi-select-dropdown', 'value'),
        State('data-table', 'data'),
        State('stored-dtypes', 'data'),
        State("stats-1d__main", "className"),
        prevent_initial_call=True
    )
    def computing_stats(columns, data, dtypes, chart_class_name):
        if columns is None:
            raise PreventUpdate

        df = pd.DataFrame(data)
        numeric_columns = []
        categorical_columns = []
        charts = []

        for col in columns:
            if is_number_type(dtypes[col]):
                numeric_columns.append(col)
                charts.extend([
                    histogram_chart(col, data),
                    box_chart(col, data),
                    violin_chart(col, data)
                ])
            else:
                categorical_columns.append(col)
                charts.extend([
                    bar_chart(col, data),
                    pie_chart(col, data)
                ])

        return (numeric_stats(numeric_columns, df) + categorical_stats(categorical_columns,df),
                charts, chart_class_name.replace("hidden", "block"))

    def numeric_stats(columns, df):
        if not columns:
            return []
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
            na_count_1d,
            median_1d,
            mean_1d,
            std_deviation_1d,
            variance_1d,
            range_1d,
            skewness_1d
        ]

        stats = [
            html.Div([
                H6(label),
                P(children=[html.Pre(f"{col}: {np.round(function(df[col]), 3)}") for col in columns])
            ])
            for label, function in zip(labels, functions)
        ]
        stats += [
            html.Div([
                H6("Kwantyle"),
                P(className="stats__paragraph", children=[
                    "¼",
                    html.Pre(children=[
                        f"{col}: {np.round(quantiles_1d(df[col], [0.25])[0.25], 3)}\n"
                        for col in columns],
                        className="stats__value"
                    ),
                ]),
                P(className="stats__paragraph", children=[
                    "½",
                    html.Pre(children=[
                        f"{col}: {np.round(quantiles_1d(df[col], [0.5])[0.5], 3)}\n"
                        for col in columns],
                        className="stats__value"
                    ),
                ]),
                P(className="stats__paragraph", children=[
                    "¾",
                    html.Pre(children=[
                        f"{col}: {np.round(quantiles_1d(df[col], [0.75])[0.75], 3)}\n"
                        for col in columns],
                        className="stats__value"
                    ),
                ]),
            ])
        ]

        return stats

    def categorical_stats(columns, df):
        if not columns:
            return []
        labels = [col for col in columns]
        functions = [na_count_1d(df[col]) for col in columns]

        stats = [
            html.Div(H6("Liczba wartości brakujących")),
            P(children=[f"{label}: {np.round(func, 3)}" for label, func in zip(labels, functions)])
        ]

        return stats

    @callback(
        Output('stats-1d__details', 'children'),
        Input('multi-select-dropdown', 'value'),
        State('data-table', 'data'),
        State('stored-dtypes', 'data'),
        prevent_initial_call=True
    )
    def generate_tables(columns, data, dtypes):
        if data is None or columns is None:
            raise PreventUpdate
        df = pd.DataFrame(data)

        numeric_columns = []
        categorical_columns = []
        tables = []

        for col in columns:
            if is_number_type(dtypes[col]):
                numeric_columns.append(col)
            else:
                categorical_columns.append(col)

        for col in numeric_columns:
            tables.append(numeric_tables(col, df))
        for col in categorical_columns:
            tables.append(categorical_tables(col, df))

        return tables

    def numeric_tables(column, df):
        values = df[column]
        mode_values = mode_1d(values)
        values_df = pd.DataFrame(
            data={
                "numeric": mode_values.index,
            },
        )

        mode_occurrences = values[values == mode_values[0]].count()
        mode_paragraph_content = "Liczba wystąpień poniższej wartości: "
        if mode_values.size > 1:
            mode_paragraph_content = "Liczba wystąpień poniższej wartości: "
        mode_paragraph_content += f"{mode_occurrences}."

        numeric_column_name = "Zmienna numeryczna"

        return html.Div(children=[
            H6(f"Moda dla {column}"),
            P(children=mode_paragraph_content),
            dag.AgGrid(
                id="stats-1d-numeric-table",
                rowData=values_df.to_dict("records"),
                columnDefs=[
                    {
                        "field": "numeric",
                        "headerName": numeric_column_name,
                    },
                ],
                style={
                    "height": min(values_df.shape[0], MAX_ROWS) * ROW_HEIGHT
                              + HEADER_ROW_HEIGHT + 2,
                    "overflow": "hidden"
                    if values_df.shape[0] <= MAX_ROWS
                    else "auto"
                }
            ),
        ])

    def categorical_tables(column, df):
        values = df[column]
        count_values = count_1d(values)
        frequency_values = (100 * proportion_1d(values)).round(decimals=1)
        values_df = pd.DataFrame(
            data={
                "categorical": count_values.index,
                "count": count_values,
                "frequency": frequency_values,
            },
        )

        categorical_column_name = "Zmienna kategoryczna"
        count_column_name = "Liczebność"
        frequency_column_name = "Częstotliwość [%]"

        return html.Div(className="mt-2", children=[
            H6(f"Liczebność i częstotliwosć dla {column}"),
            dag.AgGrid(
                id="stats-1d-categorical-table",
                rowData=values_df.to_dict("records"),
                columnDefs=[
                    {
                        "field": "categorical",
                        "headerName": categorical_column_name,
                    },
                    {
                        "field": "count",
                        "headerName": count_column_name,
                        "filter": True,
                    },
                    {
                        "field": "frequency",
                        "headerName": frequency_column_name,
                        "filter": True,
                    },
                ],
                style={
                    "height": min(values_df.shape[0], MAX_ROWS) * ROW_HEIGHT
                              + HEADER_ROW_HEIGHT + 2,
                    "overflow": "hidden"
                    if values_df.shape[0] <= MAX_ROWS
                    else "auto"
                }
            )
        ])

    def histogram_chart(column, data):
        df = pd.DataFrame(data)

        fig = px.histogram(df, x=column, nbins=10,
                           title=f'Histogram wartości dla {column}',
                           labels={'count': 'Liczba wystąpień', column: 'Wartość'})

        fig.update_layout(yaxis_title='Liczba wystąpień')

        return dcc.Graph(figure=fig)

    def bar_chart(column, data):
        df = pd.DataFrame(data)
        values = df[column]

        value_counts = values.value_counts().reset_index()
        value_counts.columns = ['Wartość', 'Liczba wystąpień']
        value_counts['Wartość'] = value_counts['Wartość'].astype(str)

        value_counts = value_counts.sort_values(by='Liczba wystąpień', ascending=False)

        fig = px.bar(value_counts, x='Wartość', y='Liczba wystąpień',
                     title=f'Liczba wystąpień każdej unikalnej wartości dla {column}')

        return dcc.Graph(figure=fig)

    def pie_chart(column, data):
        df = pd.DataFrame(data)
        values = df[column]

        value_counts = values.value_counts().reset_index()
        value_counts.columns = ['Wartość', 'Liczba wystąpień']

        fig = px.pie(value_counts, names='Wartość', values='Liczba wystąpień',
                     title=f'Procent wystąpień każdej unikalnej wartości dla {column}')

        return dcc.Graph(figure=fig)

    def box_chart(column, data):
        df = pd.DataFrame(data)
        fig = px.box(df, y=column, title=f'Wykres pudełkowy dla kolumny {column}')

        return dcc.Graph(figure=fig)

    def violin_chart(column, data):
        df = pd.DataFrame(data)
        fig = px.violin(df, y=column, title=f'Wykres skrzypcowy dla kolumny {column}')

        return dcc.Graph(figure=fig)
