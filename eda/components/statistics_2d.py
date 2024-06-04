from dash import dcc, html, callback, Input, Output, State
from dash.exceptions import PreventUpdate
import dash_ag_grid as dag

from eda.destats import *
from eda.data_table.column_type import is_number_type, is_categorical_type


def register_2d_stats_callbacks():
    MAX_ROWS = 15
    ROW_HEIGHT = 42
    HEADER_ROW_HEIGHT = 49

    @callback(
        Output('statistic_2d_output', 'children', allow_duplicate=True),
        Input('dataframe', 'data'),
        prevent_initial_call=True
    )
    def render(df_json: str):
        return html.Div(id="stats-2d", children=[
            html.H2("Statystki opisowe 2D"),
            html.Div(id="stats-2d__dropdown"),
            html.Div(id="stats-2d__summary"),
            html.Div(id="stats-2d__tables"),
        ])

    @callback(
        Output('stats-2d__dropdown', 'children'),
        Input('data-table', 'data'),
        prevent_initial_call=True
    )
    def update_dropdowns(data_table):
        df = pd.DataFrame(data_table)
        options = [{'label': col, 'value': col} for col in df.columns]
        dropdowns = [html.Div([
            html.Label(f'Wybierz kolumny, dla których chcesz obliczyć statystyki: '),
            dcc.Dropdown(options=options, id='2d-dropdown1')
        ]),
            html.Div([
                dcc.Dropdown(options=options, id='2d-dropdown2')
            ])]

        return dropdowns

    @callback(
        Output('stats-2d__summary', 'children'),
        Input('2d-dropdown1', 'value'),
        Input('2d-dropdown2', 'value'),
        State('data-table', 'data'),
        State('stored-dtypes', 'data'),
        prevent_initial_call=True
    )
    def computing_stats(x, y, data, dtypes):
        if x is None or y is None:
            raise PreventUpdate

        df = pd.DataFrame(data)

        if is_number_type(dtypes[x]) and is_number_type(dtypes[y]):
            return numeric_stats(df, x, y)
        if is_categorical_type(dtypes[x]) and is_number_type(dtypes[y]):
            return create_categorical_tables(df, x, y)

        return None

    def numeric_stats(data, x, y):
        labels = [
            "Korelacja Pearsona",
            "Korelacja Spearmana",
            "Współczynnik determinacji",
            "Współczynnik korelacji",
        ]
        x, y = clean_columns(data[x], data[y])
        functions = [
            pearson_correlation(x, y),
            spearman_correlation(x, y),
            coefficient_of_determination(x, y),
            correlation_coefficient(x, y),
        ]

        stats = [
            html.Div([
                html.H3(label + ":"),
                html.Pre(function)
            ])
            for label, function in zip(labels, functions)
        ]

        def linear_regression_wrapper(result_dict):
            return [html.Div([html.H3("Regresja liniowa:")]),
                    html.Div([f"Intercept: {result_dict.get('intercept')}"]),
                    html.Div([f"Współczynnik nachylenia: {result_dict.get('slope')}"])]

        def confidence_regression_wrapper(result_dict):
            return [html.Div([html.H3("Przedział ufności:")]),
                    html.Div([f"Przedział ufności dla interceptu: {result_dict.get('intercept')}"]),
                    html.Div([f"Przedział ufności dla współczynnika nachylenia: {result_dict.get('slope')}"])]

        result = linear_regression(x, y)
        stats.extend(linear_regression_wrapper(result))
        result = confidence_interval(x, y)
        stats.extend(confidence_regression_wrapper(result))

        return stats

    def create_categorical_tables(data, x, y):
        x_, y_ = clean_columns(data[x], data[y])
        cluster = cluster_analysis(pd.DataFrame({x: x_, y: y_}), 2)
        regression = linear_regression_analysis(x_, y_)
        df = data.rename(columns={x: 'A'})
        df = df.rename(columns={y: 'B'})
        formula = 'B ~ A'
        anova = anova_analysis(df, formula)
        ancova = ancova_analysis(df, formula)

        anova_table = dag.AgGrid(
            id="stats-anova-table",
            rowData=anova.to_dict("records"),
            columnDefs=[
                {"field": "df", "headerName": "Stopnie swobody"},
                {"field": "sum_sq", "headerName": "Suma kwadratów"},
                {"field": "mean_sq", "headerName": "Średnia kwadratów"},
                {"field": "F", "headerName": "Wartość F"},
                {"field": "PR(>F)", "headerName": "p-wartość"},
            ],
            style={
                "height": min(anova.shape[0], MAX_ROWS) * ROW_HEIGHT + HEADER_ROW_HEIGHT + 2,
                "overflow": "hidden" if anova.shape[0] <= MAX_ROWS else "auto"
            }
        )

        ancova_table = dag.AgGrid(
            id="stats-ancova-table",
            rowData=ancova.to_dict("records"),
            columnDefs=[
                {"field": "df", "headerName": "Stopnie swobody"},
                {"field": "sum_sq", "headerName": "Suma kwadratów"},
                {"field": "F", "headerName": "Wartość F"},
                {"field": "PR(>F)", "headerName": "p-wartość"},
            ],
            style={
                "height": min(ancova.shape[0], MAX_ROWS) * ROW_HEIGHT + HEADER_ROW_HEIGHT + 2,
                "overflow": "hidden" if ancova.shape[0] <= MAX_ROWS else "auto"
            }
        )

        combined_table = pd.concat([regression, cluster], axis=1)

        cluster_regression_table = dag.AgGrid(
            id="combined-results",
            rowData=combined_table.reset_index().to_dict("records"),
            columnDefs=[
                {"field": "index", "headerName": "Index"},
                {"field": "0", "headerName": "Przewidziane wyniki regresji"},
                {"field": "1", "headerName": "Klaster"},
            ],
            style={
                "height": min(combined_table.shape[0], MAX_ROWS) * ROW_HEIGHT + HEADER_ROW_HEIGHT + 2,
                "overflow": "hidden" if combined_table.shape[0] <= MAX_ROWS else "auto"
            }
        )

        return (html.H3("Analiza wariancji"), anova_table, html.H3("Analiza kowariancji"),
                ancova_table, html.H3("Analiza regresji i klasteryzacja"), cluster_regression_table)
