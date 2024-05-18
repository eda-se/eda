from dash import Dash, html

from eda.file_input.file_input import register_input_callbacks
from eda.data_table.data_table import register_dataframe_callbacks

app = Dash(__name__, suppress_callback_exceptions=True)

app.layout = html.Div([
    html.Div(id='output')
])


if __name__ == '__main__':
    register_input_callbacks()
    register_dataframe_callbacks()
    app.run(debug=True)
