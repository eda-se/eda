from dash import Dash, html, dcc

from eda.data_correction.data_correction import register_data_correction_callbacks
from eda.file_input.file_input import register_input_callbacks
from eda.data_table.data_table import register_dataframe_callbacks
from eda.components import H1
# from eda.components.graph import register_graph_callbacks
from eda.components.statistics_1d import register_1d_stats_callbacks
from eda.components.statistics_2d import register_2d_stats_callbacks

index_template = """
    <!DOCTYPE html>
    <html class="light">
        <head>
            {%metas%}
            <title>{%title%}</title>
            {%favicon%}
            <script src="https://kit.fontawesome.com/ecfb1d6b01.js" crossorigin="anonymous"></script>
            <script src="https://cdn.tailwindcss.com"></script>
            <script>
                tailwind.config = {
                    darkMode: "selector",
                };
            </script>
            {%css%}
        </head>
        <body>
            <!--[if IE]>
                <script>
                    alert(
                        "Dash v2.7+ does not support Internet Explorer. " +
                        "Please use a newer browser."
                    );
                </script>
            <![endif]-->
            {%app_entry%}
            <footer>
                {%config%}
                {%scripts%}
                {%renderer%}
            </footer>
        </body>
    </html>
"""

if __name__ == '__main__':
    app = Dash(__name__,
        title="EDA",
        index_string=index_template,
        suppress_callback_exceptions=True
    )

    app.layout = html.Div(id="main", children=[
        H1("Analiza Eksploracyjna"),
        html.Div(id="output", className="py-6"),

        html.Div(id="data_correction_output", className="py-6"),
        html.Div(id="statistic_output", className="py-6"),
        html.Div(id="statistic_2d_output", className="py-6"),
        # html.Div(id="graph_output", className="py-6"),
        html.Footer(className="h-40"),

        dcc.Store(id="dataframe"),
    ])

    register_input_callbacks()
    register_dataframe_callbacks()
    register_1d_stats_callbacks()
    register_2d_stats_callbacks()
    # register_graph_callbacks()
    register_data_correction_callbacks()

    app.run(debug=True)
