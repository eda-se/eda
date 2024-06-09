from dash import html

__H_TEXT_COLOR = "text-stone-900"


def H1(content: str) -> html.H1:
    return html.H1(
        content,
        className=f"text-4xl font-bold tracking-tight {__H_TEXT_COLOR} mb-16 sm:text-5xl"
    )


def H2(content: str) -> html.H2:
    return html.H2(
        content,
        className=f"text-2xl font-bold tracking-tight {__H_TEXT_COLOR} mb-2 sm:text-3xl"
    )


def H3(content: str) -> html.H3:
    return html.H3(
        content,
        className=f"text-xl font-bold tracking-tight {__H_TEXT_COLOR} mb-2 sm:text-2xl"
    )


def H4(content: str) -> html.H4:
    return html.H4(
        content,
        className=f"text-lg font-bold tracking-tight {__H_TEXT_COLOR} mb-2 sm:text-xl"
    )

def H6(content: str) -> html.H6:
    return html.H6(
        content,
        className=f"text-base font-bold tracking-tight {__H_TEXT_COLOR} mb-2 sm:text-base"
    )


def P(id: str | None = None, className="", children=None, margin_y=False) -> html.P:
    className += " text-stone-700"
    if margin_y:
        className += " my-2"

    if id is None:
        return html.P(
            className=className,
            children=children
        )
    return html.P(
        id=id,
        className=className,
        children=children
    )


def Button(content: str, id: str) -> html.Button:
    return html.Button(
        content,
        id=id,
        className="w-full px-6 py-2 font-medium tracking-wide text-white transition-colors duration-300 transform bg-blue-600 rounded-lg hover:bg-blue-500 focus:outline-none focus:ring focus:ring-blue-300 focus:ring-opacity-80",
        n_clicks=0
    )


def GridDiv(
    id: str | None = None,
    children: list[html.Div] | None = None,
    columns_count: int = 1
) -> html.Div:
    class_name = f"grid grid-cols-1 md:grid-cols-{columns_count // 2} lg:grid-cols-{columns_count} gap-4"

    if id is None:
        return html.Div(
            className=class_name,
            children=children
        )
    return html.Div(
        id=id,
        className=class_name,
        children=children
    )
