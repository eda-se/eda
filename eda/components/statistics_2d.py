from dash import dcc, html, callback, Input, Output, State, dash_table, no_update
from dash.exceptions import PreventUpdate
import dash_ag_grid as dag

from eda.destats import *
from eda.data_table.column_type import is_number_type, is_categorical_type


def register_2d_stats_callbacks():
    @callback(
        Output('statistic_2d_output', 'children', allow_duplicate=True),
        Input('dataframe', 'data'),
        prevent_initial_call=True
    )
    def render(df_json: str):
        return html.Div(id="stats-2d", children=[
            html.H2("Statystki opisowe 2D"),
            html.Div(id="stats-2d__dropdown"),
            html.Div(id="stats-2d__selected-variable"),
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
        Output('stats-2d__selected-variable', 'children'),
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

        info = f"Aktualnie wybrane wartości: {x}, {y}"
        df = pd.DataFrame(data)

        if is_number_type(dtypes[x]) and is_number_type(dtypes[y]):
            return info, numeric_stats(df, x, y)
        if is_categorical_type(dtypes[x]) and is_number_type(dtypes[y]):
            return info, create_statistics_table(df, x, y)

        return info, "Wybierz albo dwie wartości numeryczne, albo pierwszą kategoryczną, a drugą numeryczną!"

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

    def categorical_stats(data, x, y):
        formula = f'{y} ~ {x}'
        n_clusters = 2
        anova_results = anova_analysis(data, formula)
        ancova_results = ancova_analysis(data, formula)
        regression_predictions = linear_regression_analysis(data[x], data[y])
        cluster_labels = cluster_analysis(data, n_clusters)

        combined_results = {
            "ANOVA": anova_results.to_dict(),
            "ANCOVA": ancova_results.to_dict(),
            "Regression Predictions": regression_predictions.to_dict(),
            "Cluster Labels": cluster_labels.to_dict()
        }

        combined_df = pd.concat(
            [pd.DataFrame.from_dict(v, orient='index').reset_index() for k, v in combined_results.items()],
            keys=combined_results.keys(),
            names=['Analysis Type', 'Index']
        ).reset_index()

        return combined_df

    def create_statistics_table(data: pd.DataFrame, x: pd.Series, y: pd.Series):
        statistics_df = categorical_stats(data, x, y, )

        column_defs = [
            {"field": "Analysis Type", "headerName": "Type of Analysis"},
            {"field": "Index", "headerName": "Index"},
            {"field": "index", "headerName": "Statistic"},
            {"field": 0, "headerName": "Value"}
        ]

        return dag.AgGrid(
            id="statistics-table",
            rowData=statistics_df.to_dict("records"),
            columnDefs=column_defs,
            style={
                "height": min(statistics_df.shape[0], 20) * 28 + 30 + 2,
                "overflow": "hidden" if statistics_df.shape[0] <= 20 else "auto"
            }
        )
