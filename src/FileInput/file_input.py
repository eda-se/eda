import dash
import pandas as pd
from dash import html, dcc, callback, Input, Output
from dash.exceptions import PreventUpdate

from src.FileInput.csv_parser import get_dataframe_from_contents


def register_input_callbacks():
    @callback(
        Output('output', 'children'),
        Input('output', 'id'),
    )
    def on_render(_):
        return html.Div([
            dcc.Upload(
                id='upload-data',
                children=html.Div([
                    'Przeciągnij i upuść lub ',
                    html.A('wybierz plik')
                ]),
                style={
                    'width': '50%',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '10px'
                },
            ),
            html.Div(id='error'),
            dcc.Store(id='dataframe')
        ])

    @callback(
        [
            Output('dataframe', 'data'),
            Output('error', 'children')
        ],
        Input('upload-data', 'contents'),
    )
    def handle_file(contents):
        if contents is None:
            raise PreventUpdate

        result = get_dataframe_from_contents(contents)

        if isinstance(result, pd.DataFrame):
            return result.to_json(), dash.no_update
        else:
            return dash.no_update, html.Div(result)
