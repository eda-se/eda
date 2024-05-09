from io import StringIO

import pandas as pd
from dash import html, callback, Input, Output, dash_table


def register_dataframe_callbacks():
    @callback(
        Output('output', 'children', allow_duplicate=True),
        Input('dataframe', 'data'),
        prevent_initial_call=True
    )
    def render(df_json: str):
        df = pd.read_json(StringIO(df_json))
        return html.Div(
            dash_table.DataTable(data=df.to_dict('records'), page_size=15)
        )
