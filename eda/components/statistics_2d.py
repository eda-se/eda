from dash import dcc, html, callback, Input, Output, State, dash_table, no_update
from dash.exceptions import PreventUpdate
import dash_ag_grid as dag

from eda.destats import *
from eda.data_table.column_type import is_number_type


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
        else:
            return info, no_update

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
            return [html.Div([html.H3("Regresja liniowa" + ":")]),
                    html.Div([f"Intercept: {result_dict.get('intercept')}"]),
                    html.Div([f"Współczynnik nachylenia: {result_dict.get('slope')}"])]

        def confidence_regression_wrapper(result_dict):
            return [html.Div([html.H3("Regresja liniowa" + ":")]),
                    html.Div([f"Intercept: {result_dict.get('intercept')}"]),
                    html.Div([f"Współczynnik nachylenia: {result_dict.get('slope')}"])]

        result = linear_regression(x, y)
        stats.extend(linear_regression_wrapper(result))
        result = confidence_interval(x, y)
        stats.extend(confidence_regression_wrapper(result))

        return stats

