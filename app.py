from dash import Dash, html, dcc

from eda.file_input.file_input import register_input_callbacks
from eda.data_table.data_table import register_dataframe_callbacks
from eda.components.graph import register_graph_callbacks
from eda.components.statistics import register_1d_stats_callbacks

app = Dash(__name__, suppress_callback_exceptions=True)

app.layout = html.Div([
    html.Div(id='output'),
    html.Div(style={'height': '40px'}),
    html.Div(id='statistic_output'),
    html.Div(style={'height': '40px'}),
    html.Div(id='graph_output'),
    dcc.Store(id='dataframe'),
])

if __name__ == '__main__':
    register_input_callbacks()
    register_dataframe_callbacks()
    register_1d_stats_callbacks()
    register_graph_callbacks()
    app.run(debug=True)
