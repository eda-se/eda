from typing import NamedTuple
from dash import ctx, html, callback, Input, State, Output
from dash.exceptions import PreventUpdate

from eda.file_input.csv_parser import CSVParser
from eda.components import Button

NavigationComponent = NamedTuple("NavigationComponent", [
    ("id", str),
    ("label", str),
    ("responsible_for", str),
])
navigation_components = [
    NavigationComponent(
        label="Edycja danych",
        id="nav-data-modification",
        responsible_for="data-edition-container"
    ),
    NavigationComponent(
        label="Statystyki 1D",
        id="nav-stats-1d",
        responsible_for="statistic_output"
    ),
    NavigationComponent(
        label="Statystyki 2D",
        id="nav-stats-2d",
        responsible_for="statistic_2d_output"
    ),
]


def navigation() -> html.Div:
    return html.Div(className="flex w-full p-4 bg-zinc-50 border border-solid border-t-purple-100", children=[
        html.Div(
            className="flex gap-3 w-full max-w-2xl mx-auto",
            children=[
                html.Div(className="w-full", children=[
                    Button(nc.label, nc.id)
                ])
                for nc in navigation_components
            ]
        ),
    ])

def register_navigation_callbacks():
    @callback(
        Output("navigation", "className"),
        State("navigation", "className"),
        Input("upload-csv-data", "contents"),
        prevent_initial_call=True
    )
    def on_upload(class_name: str, content: str | None) -> str:
        if content is None:
            raise PreventUpdate
        return class_name.replace("hidden", "block")

    @callback(
        Output("data-edition-container", "className"),
        Output("statistic_output", "className"),
        Output("statistic_2d_output", "className"),
        Output("active_section_id", "data"),
        Input("nav-data-modification", "n_clicks"),
        Input("nav-stats-1d", "n_clicks"),
        Input("nav-stats-2d", "n_clicks"),
        State("data-edition-container", "className"),
        State("statistic_output", "className"),
        State("statistic_2d_output", "className"),
        State("active_section_id", "data"),
        prevent_initial_call=True
    )
    def on_button_pressed(
        ignored0, ignored1, ignored2,
        data_correction: str,
        stats_1d: str,
        stats_2d: str,
        active_section_id: str
    ):
        if ctx.triggered_id == active_section_id:
            raise PreventUpdate

        class_name_map: dict[str | int, str] = {
            navigation_components[0].id: data_correction,
            0:                           data_correction,
            navigation_components[1].id: stats_1d,
            1:                           stats_1d,
            navigation_components[2].id: stats_2d,
            2:                           stats_2d,
        }

        return_values: list[str] = [
            data_correction,
            stats_1d,
            stats_2d,
            active_section_id,
        ]

        for i, navigation_component in enumerate(navigation_components):
            if navigation_component.id == ctx.triggered_id:
                class_name = class_name_map.get(navigation_component.id, "")
                new_class_name = class_name.replace("hidden", "block")
                return_values[i] = new_class_name
                return_values[3] = navigation_component.responsible_for
            elif navigation_component.responsible_for == active_section_id:
                new_class_name = class_name_map[navigation_component.id] \
                    .replace("block", "hidden")
                return_values[i] = new_class_name

        return tuple(return_values)
