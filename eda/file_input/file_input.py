import dash
from dash import html, dcc, callback, Input, Output
from dash.exceptions import PreventUpdate

from eda.file_input.csv_parser import get_dataframe_from_contents


def register_input_callbacks():
    @callback(
        Output('output', 'children'),
        Input('output', 'id'),
    )
    def on_render(_):
        return html.Div(children=[
            dcc.Upload(
                id='upload-csv-data',
                className="upload-container w-full max-w-xl",
                children=[
                    html.Label(className="flex flex-col items-center w-full p-5 text-center bg-white border-2 border-purple-200 border-dashed cursor-pointer dark:bg-gray-900 dark:border-gray-700 rounded-xl hover:bg-slate-50 hover:border-blue-600 ease-in-out duration-200", children=[
                        html.I(className="fa-solid fa-cloud-arrow-up text-2xl text-gray-500 dark:text-gray-400"),
                        html.H2("Dodaj swój arkusz kalkulacyjny", className="mt-1 font-medium tracking-wide text-gray-700 dark:text-gray-200"),
                        html.P("Wybierz lub przeciągnij i upuść plik CSV", className="mt-2 text-xs tracking-wide text-gray-500 dark:text-gray-400")
                    ])
                ]
            ),
            html.Div(id='upload-error')
        ])

    @callback(
        [
            Output('dataframe', 'data'),
            Output('upload-error', 'children')
        ],
        Input('upload-csv-data', 'contents'),
    )
    def handle_file(content: str | None):
        if content is None:
            raise PreventUpdate

        try:
            result = get_dataframe_from_contents(content)
            return result.to_json(), dash.no_update
        except TypeError as e:
            return dash.no_update, html.Div(str(e))
