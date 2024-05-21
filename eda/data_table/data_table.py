from io import StringIO

import pandas as pd
from dash import html, callback, Input, Output, dash_table, dcc, State, exceptions, ALL, no_update
from eda.data_table.column_type_converter import covert_column_data_type


def register_dataframe_callbacks():
    @callback(
        Output('output', 'children', allow_duplicate=True),
        Input('dataframe', 'data'),
        prevent_initial_call=True
    )
    def render(df_json: str):
        df = pd.read_json(StringIO(df_json))

        return html.Div([
            dcc.Store(id='stored-dataframe', data=df.to_json(date_format='iso')),
            dcc.Store(id='stored-dtypes', data=df.dtypes.astype(str).to_dict()),

            dash_table.DataTable(id='data-table', data=df.to_dict('records'), page_size=15),

            html.Div(id='dropdown-container'),

            html.Button('Zapisz zmiany', id='save', n_clicks=0),
            html.Button('Cofnij wszystkie zmiany', id='reset', n_clicks=0),

            html.Div(id='dropdown_output')
        ])

    @callback(
        Output('dropdown-container', 'children'),
        Input('stored-dtypes', 'data')
    )
    def update_dropdowns(stored_data_types):
        dropdowns = []
        for column, type in stored_data_types.items():
            if 'datetime64' in type:
                type = 'datetime64'
            dropdowns.append(
                html.Div([
                    html.Label(f'Wybierz typ dla {column}'),
                    dcc.Dropdown(
                        id={'type-dropdown': column},
                        options=[
                            {'label': 'String', 'value': 'object'},
                            {'label': 'Integer', 'value': 'int64'},
                            {'label': 'Float', 'value': 'float64'},
                            {'label': 'Datetime', 'value': 'datetime64'},
                            {'label': 'Categorical', 'value': 'category'},
                        ],
                        value=type
                    )
                ])
            )
        return dropdowns

    @callback(
        Output('dropdown_output', 'children'),
        Output('data-table', 'data'),
        Output('stored-dtypes', 'data'),
        [Input({'type-dropdown': ALL}, 'value')],
        [Input({'type-dropdown': ALL}, 'id'),
         State('data-table', 'data'),
         State('stored-dtypes', 'data')],
        prevent_initial_call=True
    )
    def update_data_types(selected_values, column_ids, data_table_data, stored_dtypes):
        df = df = pd.DataFrame(data_table_data)
        columns = [c["type-dropdown"] for c in column_ids]

        for col, dtype in zip(columns, selected_values):
            try:
                covert_column_data_type(df, col, dtype)
                stored_dtypes[col] = dtype

            except Exception as e:
                return f"Error converting column {col} to {dtype}: \n{str(e)}", no_update, no_update

        return "Poprawnie wybrane typy", df.to_dict('records'), stored_dtypes

    @callback(
        Output('data-table', 'data', allow_duplicate=True),
        Output('stored-dtypes', 'data', allow_duplicate=True),
        Input('reset', 'n_clicks'),
        State('stored-dataframe', 'data'),
        prevent_initial_call=True
    )
    def reset_data(n_clicks, stored_df_json):
        df = pd.read_json(StringIO(stored_df_json))
        data_types = df.dtypes.astype(str).to_dict()
        return df.to_dict('records'), data_types

    @callback(
        Output('stored-dataframe', 'data'),
        Input('save', 'n_clicks'),
        State('data-table', 'data'),
        prevent_initial_call=True
    )
    def save_data(n_clicks, data_table_data):
        df = pd.DataFrame(data_table_data)
        return df.to_json(date_format='iso')
