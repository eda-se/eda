from io import StringIO

from dash import dcc, html, callback, Input, Output, State, dash_table, no_update
from dash.exceptions import PreventUpdate
import dash_ag_grid as dag
import plotly.express as px
from pandas.core.dtypes.common import is_numeric_dtype


from eda.destats import *
from eda.components import H2, H3, H6, P, Button, GridDiv


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

            html.Div(id="stats-1d__dropdown"),

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
        Output('stats-1d__dropdown', 'children'),
        Input('data-table', 'data'),
        prevent_initial_call=True
    )
    def update_dropdowns(data_table):
        df = pd.DataFrame(data_table)
        options = [{'label': col, 'value': col} for col in df.columns]
        dropdown = html.Div([
            H3("Wybór zmiennej"),
            dcc.Dropdown(
                id="1d-dropdown",
                options=options,
                placeholder="Zmienna"
            )
        ])

        return dropdown

    @callback(
        Output('stats-1d__summary', 'children'),
        Output('stats-1d__charts', 'children'),
        Output("stats-1d__main", "className"),
        Input('1d-dropdown', 'value'),
        State('data-table', 'data'),
        State("stats-1d__main", "className"),
        prevent_initial_call=True
    )
    def computing_stats(col, data, chart_class_name):
        if col is None:
            raise PreventUpdate

        df = pd.DataFrame(data)
        values = df[col]

        if is_numeric_dtype(values):
            charts = [
                histogram_chart(col, data),
                box_chart(col, data),
                violin_chart(col, data)
            ]
            return numeric_stats(values), charts, chart_class_name.replace("hidden", "block")
        else:
            charts = [
                bar_chart(col, data),
                pie_chart(col, data)
            ]
            return categorical_stats(values), charts, chart_class_name.replace("hidden", "block")

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
                H6(label),
                P(children=html.Pre(np.round(function, 3)))
            ])
            for label, function in zip(labels, functions)
        ]
        stats += [
            html.Div([
                H6("Kwantyle"),
                P(className="stats__paragraph", children=[
                    "¼",
                    html.Pre(
                        np.round(quantile_values[0.25], 3),
                        className="stats__value"
                    ),
                ]),
                P(className="stats__paragraph", children=[
                    "½",
                    html.Pre(
                        np.round(quantile_values[0.5], 3),
                        className="stats__value"
                    ),
                ]),
                P(className="stats__paragraph", children=[
                    "¾",
                    html.Pre(
                        np.round(quantile_values[0.75], 3),
                        className="stats__value"
                    ),
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
                H6(label),
                P(children=html.Pre(np.round(function, 3)))
            ])
            for label, function in zip(labels, functions)
        ]

        return stats

    @callback(
        Output('stats-1d__details', 'children'),
        Input('1d-dropdown', 'value'),
        State('data-table', 'data'),
        prevent_initial_call=True
    )
    def generate_tables(col, data):
        if data is None or col is None:
            raise PreventUpdate

        df = pd.DataFrame(data)
        values = df[col]

        if is_numeric_dtype(values):
            return numeric_tables(values)
        return categorical_tables(values)

    def numeric_tables(values):
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
            H6("Moda"),
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

    def categorical_tables(values):
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
            H6("Liczebność i częstotliwosć"),
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

        fig = px.histogram(df, x=column, nbins=10,  # You can adjust 'nbins' as needed
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
