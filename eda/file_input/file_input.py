import dash
import pandas as pd
from dash import html, dcc, callback, Input, Output
from dash.exceptions import PreventUpdate

from eda.file_input.csv_parser import get_dataframe_from_contents


def register_input_callbacks():
    @callback(
        Output('output', 'children'),
        Input('output', 'id'),
    )
    def on_render(_):
        return html.Div([
            dcc.Upload(
                id='upload-data',
                className="file-dropdown",
                children=html.Div(children=[
                    'Przeciągnij i upuść lub ',
                    html.A('wybierz plik')
                ]),
                style={
                    'width': '50%',
                    'height': '60px',
                    'lineHeight': '60px',
                    'margin': '10px'
                },
            ),
            html.Div(id='error')
        ])

    @callback(
        [
            Output('dataframe', 'data'),
            Output('error', 'children')
        ],
        Input('upload-data', 'contents'),
    )
    def handle_file(content: str | None):
        if content is None:
            raise PreventUpdate

        try:
            result = get_dataframe_from_contents(content)
            return result.to_json(), dash.no_update
        except TypeError as e:
            return dash.no_update, html.Div(str(e))
