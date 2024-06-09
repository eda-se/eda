from dash import dcc, html, callback, Input, Output, State, no_update
from dash.exceptions import PreventUpdate

from eda.destats import *
from eda.data_table.column_type import is_number_type
from eda.components import H2, H3, H6, P, GridDiv


def register_2d_stats_callbacks():
    @callback(
        Output("statistic_2d_output", "children", allow_duplicate=True),
        Input("dataframe", "data"),
        prevent_initial_call=True
    )
    def render(df_json: str):
        return html.Div(id="stats-2d", children=[
            H2("Statystki opisowe 2D"),
            H3("Wybór zmiennych"),
            GridDiv(id="stats-2d__dropdown", columns_count=4),
            GridDiv(id="stats-2d__summary", columns_count=5),
            html.Div(id="stats-2d__tables"),
            html.Div(id='stats-2d__buttons'),
            html.Div(id='stats-2d__chart'),
            html.Div(id='stats-2d__reverse'),
        ])

    @callback(
        Output("stats-2d__dropdown", "children"),
        Input("data-table", "data"),
        prevent_initial_call=True
    )
    def update_dropdowns(data_table):
        df = pd.DataFrame(data_table)
        options = [{"label": col, "value": col} for col in df.columns]

        return [
            dcc.Dropdown(options=options, id="2d-dropdown1", placeholder="Pierwsza zmienna"),
            dcc.Dropdown(options=options, id="2d-dropdown2", placeholder="Druga zmienna"),
        ]

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
        else:
            return no_update

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
                H6(label),
                html.Pre(np.round(function, 3))
            ])
            for label, function in zip(labels, functions)
        ]

        def linear_regression_wrapper(result_dict):
            return html.Div(children=[
                H6("Regresja liniowa"),
                P(children=[
                    html.Span("Współczynnik nachylenia: ", className="text-stone-900"),
                    html.Pre(np.round(result_dict.get("slope"), 3)),
                ]),
                P(children=[
                    html.Span("Przecięcie: ", className="text-stone-900"),
                    html.Pre(np.round(result_dict.get("intercept"), 3)),
                ]),
            ]),

        def confidence_regression_wrapper(result_dict):
            slope = np.round(result_dict.get('slope'), 3)
            intercept = np.round(result_dict.get('intercept'), 3)
            return html.Div(children=[
                H6("Przedział ufności"),
                P(children=[
                    html.Span("Przedział ufności dla współczynnika nachylenia: ", className="text-stone-900"),
                    html.Pre(f"[{slope[0]}, {slope[1]}]"),
                ]),
                P(children=[
                    html.Span("Przedział ufności dla przecięcia: ", className="text-stone-900"),
                    html.Pre(f"[{intercept[0]}, {intercept[1]}]"),
                ]),
            ]),

        result = linear_regression(x, y)
        stats.extend(linear_regression_wrapper(result))
        result = confidence_interval(x, y)
        stats.extend(confidence_regression_wrapper(result))

        return stats
