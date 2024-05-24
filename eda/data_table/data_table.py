from io import StringIO

import pandas as pd
from dash import (
    html,
    callback,
    Input,
    Output,
    dash_table,
    dcc,
    State,
    ALL,
    no_update,
)

from eda.data_table.column_type import (
    convert_column_data_type,
    is_int_column,
    is_float_column,
)


def register_dataframe_callbacks():
    @callback(
        Output('output', 'children', allow_duplicate=True),
        Input('dataframe', 'data'),
        prevent_initial_call=True
    )
    def render(df_json: str):
        df = pd.read_json(StringIO(df_json))

        for name, values in df.items():
            if values.dtype == "object" or values.dtype == "float64":
                if is_int_column(values):
                    convert_column_data_type(df, name, "int64")
                elif is_float_column(values):
                    convert_column_data_type(df, name, "float64")

        string_dtypes = df.dtypes.astype(str).str.lower()
        json_dataframe = df.to_json(date_format="iso")

        return html.Div([
            dcc.Store(id='current-dtypes', data=string_dtypes.to_dict()),
            dcc.Store(id='stored-dtypes', data=string_dtypes.to_dict()),
            dcc.Store(id='stored-dataframe', data=json_dataframe),

            html.H2("Zaimportowany plik CSV"),
            dash_table.DataTable(
                id="data-table",
                columns=[
                    {
                        "name": name,
                        "id": name,
                        "deletable": True,
                        "renamable": True,
                    }
                    for name in df.columns.tolist()
                ],
                data=df.to_dict("records"),
                page_size=15,
            ),

            html.H2("Edytor zmiennych"),
            html.Div(id='dropdown-container'),

            html.Button('Zapisz zmiany', id='save', n_clicks=0),
            html.Button('Cofnij wszystkie zmiany', id='reset', n_clicks=0),

            html.Div(id='dropdown_status')
        ])


    @callback(
        Output('dropdown-container', 'children'),
        Input('current-dtypes', 'data'),
        Input('data-table', 'columns')
    )
    def update_dropdowns(current_data_types, data_table_columns):
        dropdowns = []
        for column in data_table_columns:
            column_name = column['name']
            column_id = column['id']

            column_type = current_data_types[column_id]
            if 'datetime64' in column_type:
                column_type = 'datetime64'

            dropdowns.append(
                html.Div([
                    html.Label(f'Wybierz typ dla {column_name}'),
                    dcc.Dropdown(
                        id={'type-dropdown': column_name},
                        options=[
                            {'label': 'String', 'value': 'object'},
                            {'label': 'Integer', 'value': 'int64'},
                            {'label': 'Float', 'value': 'float64'},
                            {'label': 'Datetime', 'value': 'datetime64'},
                            {'label': 'Categorical', 'value': 'category'},
                        ],
                        value=column_type
                    )
                ])
            )
        return dropdowns

    @callback(
        Output('dropdown_status', 'children'),
        Output('data-table', 'data'),
        Output('current-dtypes', 'data', allow_duplicate=True),
        Input({'type-dropdown': ALL}, 'value'),
        Input({'type-dropdown': ALL}, 'id'),
        State('data-table', 'data'),
        State('data-table', 'columns'),
        State('current-dtypes', 'data'),
        prevent_initial_call=True
    )
    def update_data_types(selected_values, column_ids, data_table_data, data_table_columns, current_data_types):
        df = pd.DataFrame(data_table_data)

        for column, dtype in zip(data_table_columns, selected_values):
            column_id = column['id']
            try:
                convert_column_data_type(df, column_id, dtype)
                current_data_types[column_id] = dtype

            except Exception as e:
                return f"Error converting column {column['name']} to {dtype}: \n{str(e)}", no_update, no_update

        return "Poprawnie wybrane typy", df.to_dict('records'), current_data_types

    @callback(
        Output('data-table', 'data', allow_duplicate=True),
        Output('data-table', 'columns', allow_duplicate=True),
        Output('current-dtypes', 'data', allow_duplicate=True),
        Input('reset', 'n_clicks'),
        State('stored-dataframe', 'data'),
        State('stored-dtypes', 'data'),
        prevent_initial_call=True
    )
    def reset_data(n_clicks, stored_df_json, stored_data_types):
        df = pd.read_json(StringIO(stored_df_json))
        columns=[
            {
                'name': name,
                'id': name,
                'deletable': True,
                'renamable': True,
            }
            for name in df.columns.tolist()
        ]

        return df.to_dict('records'), columns, stored_data_types


    @callback(
        Output('stored-dataframe', 'data'),
        Output('stored-dtypes', 'data'),
        Input('save', 'n_clicks'),
        State('data-table', 'data'),
        State('data-table', 'columns'),
        State('current-dtypes', 'data'),
        prevent_initial_call=True
    )
    def save_data(n_clicks, data_table_data, data_table_columns, current_data_types):
        id_to_name = {col['id']: col['name'] for col in data_table_columns}

        df = pd.DataFrame(data_table_data)
        df.rename(columns=id_to_name, inplace=True)
        stored_data_types = {
            id_to_name[key]: val
            for key, val in current_data_types.items() if key in id_to_name
        }

        return df.to_json(date_format='iso'), stored_data_types
