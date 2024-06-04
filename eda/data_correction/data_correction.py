import pandas as pd
from dash import html, dcc, callback, Input, Output, no_update, State, dash_table
from dash.exceptions import PreventUpdate
from pandas.core.dtypes.common import is_numeric_dtype

from eda.data_correction.missing_values import handle_missing_values
from eda.data_correction.outliers import handle_outliers


def register_data_correction_callbacks():
    @callback(
        Output("data_correction_output", "children"),
        Input("data-table", "data"),
        prevent_initial_call=True,
    )
    def data_correction(df):
        df = pd.DataFrame(df)
        return html.Div([
            missing_values_dropdown(df),
            outliers_dropdown(df),
        ])

    @callback(
        Output("missing-values-method", "options"),
        Input("missing-values-column", "value"),
        State("data-table", "data"),
    )
    def method_dropdown(column, df):
        if column:
            df = pd.DataFrame(df)
            options = [
                {"label": "Kopiuj poprzednią wartość", "value": "ffill"},
                {"label": "Zastąp najczęściej występującą wartością", "value": "most_frequent"},
                {"label": "Usuń wiersze z brakującymi wartościami", "value": "delete"},
            ]
            if is_numeric_dtype(df[column]):
                options.append({"label": "Zastąp średnią", "value": "mean"})
                options.append({"label": "Zastąp medianą", "value": "median"})

            return options
        else:
            raise PreventUpdate

    @callback(
        Output("data-table", "data", allow_duplicate=True),
        Input("missing-values-button", "n_clicks"),
        State("missing-values-column", "value"),
        State("missing-values-method", "value"),
        State("custom-missing-value", "value"),
        State("data-table", "data"),
        prevent_initial_call=True,
    )
    def button_callback(n_clicks, column, method, missing_values, df):
        if n_clicks and column and method and n_clicks > 0:
            df = pd.DataFrame(df)
            return handle_missing_values(df, column, method, missing_values=missing_values).to_dict("records")
        else:
            return no_update

    @callback(
        Output("data-table", "data", allow_duplicate=True),
        Input("outliers-button", "n_clicks"),
        State("outliers-column", "value"),
        State("outliers-find-method", "value"),
        State("outliers-fix-method", "value"),
        State("data-table", "data"),
        prevent_initial_call=True,
    )
    def button_callback(n_clicks, columns, find_method, fix_method, df):
        if n_clicks and columns and n_clicks > 0:
            df = pd.DataFrame(df)
            return handle_outliers(df, columns, find_method, fix_method).to_dict("records")
        else:
            return no_update

    @callback(
        Output("missing-values-table", "data", allow_duplicate=True),
        Input("data-table", "data"),
        prevent_initial_call=True,
    )
    def table_data(data):
        df = pd.DataFrame(data)
        return [{"col": col, "number": df[col].isna().sum()} for col in df.columns]


def missing_values_dropdown(df: pd.DataFrame) -> html.Div:
    col_options = [{"label": col, "value": col} for col in df.columns]

    number_of_missing_values = [{"col": col, "number": df[col].isna().sum()} for col in df.columns]

    return html.Div([
        html.H2("Uzupełnianie brakujących wartości"),
        dash_table.DataTable(
            id="missing-values-table",
            data= number_of_missing_values,
            columns=[
                {"name": "Kolumna", "id": "col"},
                {"name": "Liczba wartości brakujących", "id": "number"},
            ],
        ),
        html.Label(f'Wybierz kolumnę: '),
        dcc.Dropdown(options=col_options, id='missing-values-column'),
        html.Label(f'Wybierz metodę: '),
        dcc.Dropdown(id='missing-values-method'),
        dcc.Input(value="", placeholder="Niestandardowa wartość do zastąpienia", id="custom-missing-value"),
        html.Br(),
        html.Button('Uzupełnij wartości brakujące', id='missing-values-button'),
    ])


def outliers_dropdown(df: pd.DataFrame) -> html.Div:
    col_options = []
    for col in df.columns:
        if is_numeric_dtype(df[col]):
            col_options.append({"label": col, "value": col})

    find_method_options = [
        {"label": "Według 3 sigm", "value": "zscore"},
        {"label": "Według reguły 1.5 IQR", "value": "iqr"}
    ]

    fix_method_options = [
        {"label": "Usuń wartości", "value": "remove"},
        {"label": "Ogranicz wartości", "value": "cap"},
        {"label": "Zastąp średnią", "value": "mean"},
        {"label": "Zastąp medianą", "value": "median"},
    ]

    return html.Div([
        html.H2("Poprawa wartości odstających"),
        html.Label(f'Wybierz kolumny: '),
        dcc.Dropdown(options=col_options, id='outliers-column', multi=True),
        html.Label(f'Wybierz metodę: '),
        dcc.Dropdown(options=find_method_options, id='outliers-find-method', placeholder="Znajdywanie wartości odstających"),
        dcc.Dropdown(options=fix_method_options, id='outliers-fix-method', placeholder="Poprawa wartości odstających"),
        html.Button('Popraw wartości odstające w wybranych kolumnach', id='outliers-button'),

        html.Div(style={'marginBottom': '100px'})  # tymczasowe
    ])
