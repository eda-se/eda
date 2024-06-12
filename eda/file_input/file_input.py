import dash
from dash import html, dcc, callback, Input, State, Output
from dash.exceptions import PreventUpdate

from eda.file_input.csv_parser import CSVParser
from eda.data_table.column_type import (
    convert_dataframe_float_columns_to_int,
    get_types_from_dataframe
)
from eda.components import P, GridDiv


def register_input_callbacks():
    @callback(
        Output("upload-container", "children"),
        Input("upload-container", "id"),
    )
    def on_render(_):
        return html.Div(className="flex flex-col", children=[
            html.Div(className="mx-auto w-full max-w-2xl", children=[
                GridDiv(columns_count=2, children=[
                    html.Div(children=[
                        P(children="Wybierz separator kolumn"),
                        dcc.Dropdown(
                            id="file-column-separator",
                            options=[
                                {
                                    "label": separator,
                                    "value": separator,
                                }
                                for separator in [";", ","]
                            ],
                            value=";",
                            placeholder="Seprator kolumn",
                            searchable=False,
                            clearable=False
                        ),
                    ]),
                    html.Div(children=[
                        P(children="Wybierz separator dziesiętny"),
                        dcc.Dropdown(
                            id="file-decimal-separator",
                            options=[
                                {
                                    "label": separator,
                                    "value": separator,
                                }
                                for separator in [",", "."]
                            ],
                            value=",",
                            placeholder="Seprator dziesiętny",
                            searchable=False,
                            clearable=False
                        ),
                    ]),
                ]),
            ]),
            dcc.Upload(
                id='upload-csv-data',
                className="upload-container w-full max-w-xl mt-8 mx-auto",
                children=[
                    html.Label(className="flex flex-col items-center w-full p-5 text-center bg-white border-2 border-purple-200 border-dashed cursor-pointer dark:bg-gray-900 dark:border-gray-700 rounded-xl hover:bg-slate-50 hover:border-blue-600 ease-in-out duration-200", children=[
                        html.I(className="fa-solid fa-cloud-arrow-up text-2xl text-gray-500 dark:text-gray-400"),
                        html.H2("Dodaj swój arkusz kalkulacyjny", className="mt-1 font-medium tracking-wide text-gray-700 dark:text-gray-200"),
                        html.P("Wybierz lub przeciągnij i upuść plik CSV", className="mt-2 text-xs tracking-wide text-gray-500 dark:text-gray-400")
                    ])
                ]
            ),
            html.Div(id='upload-error'),
        ])

    @callback(
        Output("file_column_separator", "data"),
        Input("file-column-separator", "value")
    )
    def on_column_separator_change(separator: str) -> str:
        return separator

    @callback(
        Output("file_decimal_separator", "data"),
        Input("file-decimal-separator", "value")
    )
    def on_decimal_separator_change(separator: str) -> str:
        return separator

    @callback(
        Output("dataframe", "data"),
        Output("base_dtypes", "data"),
        Output("upload-error", "children"),
        Input("upload-csv-data", "contents"),
        State("file_column_separator", "data"),
        State("file_decimal_separator", "data")
    )
    def handle_file(
        content: str | None,
        column_separator: str,
        decimal_separator: str
    ):
        if content is None:
            raise PreventUpdate

        try:
            parser = CSVParser(column_separator, decimal_separator)
            result = parser.get_dataframe_from_contents(content)
            convert_dataframe_float_columns_to_int(result)
            types = get_types_from_dataframe(result)
            return result.to_json(), types, dash.no_update
        except TypeError as e:
            return dash.no_update, dash.no_update, html.Div(str(e))
