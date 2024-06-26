import pandas as pd
from pandas.core.dtypes.common import is_numeric_dtype
from dash import (
  html,
  dcc,
  callback,
  Input,
  Output,
  no_update,
  State,
)
from dash.exceptions import PreventUpdate
import dash_ag_grid as dag

from eda.data_correction.missing_values import handle_missing_values
from eda.data_correction.outliers import handle_outliers
from eda.components import H2, H3, H4, Button, GridDiv


def register_data_correction_callbacks():
    @callback(
        Output("data-correction-container", "children"),
        Input("data-table", "data"),
        prevent_initial_call=True,
    )
    def data_correction(df):
        df = pd.DataFrame(df)
        return html.Div([
            H2("Poprawa danych"),
            missing_values_dropdown(df),
            outliers_dropdown(df),
        ])

    @callback(
        Output("missing-values-method", "options"),
        Input("missing-values-column", "value"),
        State("data-table", "data"),
    )
    def method_dropdown(columns, df):
        if columns:
            df = pd.DataFrame(df)
            numeric_only = True
            for column in columns:
                if not is_numeric_dtype(df[column]):
                    numeric_only = False

            options = [
                {"label": "Kopiuj poprzednią wartość", "value": "ffill"},
                {"label": "Zastąp najczęściej występującą wartością", "value": "most_frequent"},
                {"label": "Usuń wiersze z brakującymi wartościami", "value": "delete"},
            ]
            if numeric_only:
                options.append({"label": "Zastąp średnią", "value": "mean"})
                options.append({"label": "Zastąp medianą", "value": "median"})

            return options
        else:
            return []

    @callback(
        Output("data-table", "data", allow_duplicate=True),
        Input("missing-values-button", "n_clicks"),
        State("missing-values-column", "value"),
        State("missing-values-method", "value"),
        State("custom-missing-value", "value"),
        State("data-table", "data"),
        prevent_initial_call=True,
    )
    def button_callback(n_clicks, columns, method, missing_values, df):
        if n_clicks and columns and method and n_clicks > 0:
            df = pd.DataFrame(df)
            for column in columns:
                df = handle_missing_values(df, column, method, missing_values=missing_values)
            return df.to_dict("records")
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
        Output("missing-values-table", "rowData"),
        Input("data-table", "data")
    )
    def table_data(data):
        df = pd.DataFrame(data)
        table_data_list = []
        for col in df.columns:
            missing = df[col].isna()
            missing_list = []
            for i in range(len(missing)):
                if missing[i]:
                    missing_list.append(str(i))
            rows = ", ".join(missing_list)
            print(rows)

            table_data_list.append({
                "col": col,
                "number": missing.sum(),
                "rows": rows,
            })
        return table_data_list


def missing_values_dropdown(df: pd.DataFrame) -> html.Div:
    col_options = [{"label": col, "value": col} for col in df.columns]
    number_of_missing_values = [{"col": col, "number": df[col].isna().sum()} for col in df.columns]

    return html.Div(className="py-2", children=[
        H3("Uzupełnianie brakujących wartości"),

        dag.AgGrid(
            id="missing-values-table",

            # rowData=number_of_missing_values,
            columnDefs=[
                {
                    "field": "col",
                    "headerName": "Zmienna",
                    "filter": True,
                    "resizable": False,
                },
                {
                    "field": "number",
                    "headerName": "Liczba wartości brakujących",
                    "minWidth": 300,
                    "filter": True,
                    "resizable": False,
                },
                {
                    "field": "rows",
                    "headerName": "Numer rekordu z brakującymi wartościami",
                    "minWidth": 300,
                    "filter": False,
                    "resizable": False,
                },
            ]
        ),

        html.Div(className="py-2", children=[
            html.Div(className="py-2", children=[
                H4(f"Wybierz zmienne"),
                GridDiv(columns_count=4, children=[
                    dcc.Dropdown(id="missing-values-column", options=col_options, placeholder="Zmienna", multi=True),
                ]),
            ]),
            html.Div(className="py-2", children=[
                H4(f"Wybierz metodę"),
                GridDiv(columns_count=4, children=[
                    dcc.Dropdown(id="missing-values-method", placeholder="Metoda"),
                    dcc.Input(
                        id="custom-missing-value",
                        className="block w-full placeholder-gray-400/70 dark:placeholder-gray-500 rounded-lg border border-gray-200 bg-white px-3 py-1.5 text-gray-700 focus:border-blue-400 focus:outline-none focus:ring focus:ring-blue-300 focus:ring-opacity-40 dark:border-gray-600 dark:bg-gray-900 dark:text-gray-300 dark:focus:border-blue-300",
                        placeholder="Niestandardowa wartość do zastąpienia"
                    ),
                ]),
            ]),
            html.Div(className="max-w-80 mt-4", children=[
                Button("Uzupełnij wartości brakujące", id="missing-values-button"),
            ]),
        ]),
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

    return html.Div(className="py-2", children=[
        H3("Poprawa wartości odstających"),

        html.Div(className="py-2", children=[
            H4("Wybierz zmienne"),
            dcc.Dropdown(id="outliers-column", options=col_options, placeholder="Zmienna", multi=True),
        ]),
        html.Div(className="py-2", children=[
            H4(f"Wybierz metodę"),
            GridDiv(columns_count=4, children=[
                dcc.Dropdown(id="outliers-find-method", options=find_method_options, placeholder="Metoda znajdowania"),
                dcc.Dropdown(id="outliers-fix-method", options=fix_method_options, placeholder="Metoda uzupełnienia"),
            ]),
        ]),

        html.Div(className="max-w-80 mt-4", children=[
            Button("Popraw wartości odstające", id="outliers-button"),
        ]),
    ])
