from dash import dcc, html, callback, Input, Output, State, no_update
from dash.exceptions import PreventUpdate
import dash_ag_grid as dag
from pandas.core.dtypes.common import is_numeric_dtype

from eda.destats import *
from eda.data_table.column_type import (
    is_numeric_type,
    is_categorical_type
)
from eda.components import H2, H3, H6, P, GridDiv


def register_2d_stats_callbacks():
    MAX_ROWS = 15
    ROW_HEIGHT = 42
    HEADER_ROW_HEIGHT = 49

    @callback(
        Output("statistic_2d_output", "children", allow_duplicate=True),
        Input("dataframe", "data"),
        prevent_initial_call=True
    )
    def render(df_json: str):
        df = pd.read_json(df_json)
        return html.Div(id="stats-2d", children=[
            H2("Statystki opisowe 2D"),
            H3("Wybór zmiennych"),
            GridDiv(id="stats-2d__dropdown", columns_count=4),

            html.Div(id="stats-2d__main", className="py-4 hidden", children=[
                GridDiv(id="stats-2d__summary", columns_count=5),
                html.Div(id="stats-2d__tables"),
                html.Div([
                    html.Label("Wybierz zakres wierszy:"),
                    dcc.Input(id='start-row', type='number', placeholder='Początkowy wiersz', min=0, max=len(df) - 1,
                            value=0),
                    dcc.Input(id='end-row', type='number', placeholder='Końcowy wiersz', min=0, max=len(df) - 1,
                            value=len(df) - 1)
                ]),
                html.Div(id='stats-2d__charts'),
                html.Div(id='stats-2d__reverse'),
            ]),
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
        Output("stats-2d__main", "className"),
        Input('2d-dropdown1', 'value'),
        Input('2d-dropdown2', 'value'),
        State('data-table', 'data'),
        State("stored-dtypes", "data"),
        State("stats-2d__main", "className"),
        prevent_initial_call=True
    )
    def computing_stats(
        x,
        y,
        data,
        dtypes: dict[str, str],
        container_class_name: str
    ):
        if x is None or y is None:
            raise PreventUpdate

        df = pd.DataFrame(data)
        class_name = container_class_name.replace("hidden", "block")

        if is_numeric_type(dtypes[x]) and is_numeric_type(dtypes[y]):
            return numeric_stats(df, x, y), class_name

        is_num_cat \
            =  is_categorical_type(dtypes[x]) and is_numeric_dtype(dtypes[y]) \
            or is_categorical_type(dtypes[y]) and is_numeric_dtype(dtypes[x])
        if (is_num_cat):
            if is_categorical_type(dtypes[y]):
                x, y = y, x
            return create_categorical_tables(df, x, y), class_name

        return no_update, no_update

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

        def linear_regression_wrapper(regression, confidence):
            slope_confidence = np.round(confidence.get('slope'), 3)
            intercept_confidence = np.round(confidence.get('intercept'), 3)
            return html.Div(children=[
                H6("Regresja liniowa"),
                P(children=[
                    html.Span("Współczynnik nachylenia: ", className="text-stone-900"),
                ]),
                html.Pre(
                    f"{np.round(regression.get('intercept'), 3)}, ",
                    className="inline"
                ),
                html.Pre(
                    f"[{intercept_confidence[0]}, {intercept_confidence[1]}]",
                    className="confidence"
                ),
                # html.Span("95% przedział ufności", className="text-xs text-stone-700"),
                P(className="mt-4", children=[
                    html.Span("Przecięcie: ", className="text-stone-900"),
                ]),
                html.Pre(
                    f"{np.round(regression.get('slope'), 3)}, ",
                    className="inline"
                ),
                html.Pre(
                    f"[{slope_confidence[0]}, {slope_confidence[1]}]",
                    className="confidence"
                ),
            ]),

        regression = linear_regression(x, y)
        confidence = confidence_interval(x, y)
        stats.extend(linear_regression_wrapper(regression, confidence))

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
