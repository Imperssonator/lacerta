from bokeh.models import ColumnDataSource
from bokeh.plotting import figure


def scatterplot(
    data,
    x,
    y,
    x_label=None,
    y_label=None,
    title=None,
    width=400,
    height=572,
    tools="hover,save,reset,wheel_zoom,pan",
    toolbar_location="right",
    active_scroll="wheel_zoom",
    tooltips=None,
    marker="circle",
    marker_size=8,
    marker_alpha=0.6,
    axis_label_font_size="10pt",
    marker_label_font_size="8pt",
    **kwargs
):
    """
    Basic interactive scatterplot with strong defaults.

    Parameters
    ----------
    data: pd.DataFrame
    x: str
    y: str
    x_label: str
    y_label: str
    title: str
    width: int
    height: int
    tools: str
    toolbar_location: str
    active_scroll: str
    tooltips: List(Tuple(str,str))
    marker: str
    marker_size: float
    marker_alpha: float
    kwargs:
        Additional arguments for bokeh figure.scatter()
    """

    cds = ColumnDataSource(data)
    headers = data.columns

    if x_label is None:
        x_label = x
    if y_label is None:
        y_label = y
    
    if tooltips is None:
        tooltips = [
            (hh, f'@{{{hh}}}') for hh in headers
        ]

    p = figure(
        title=title,
        x_axis_label=x_label,
        y_axis_label=y_label,
        width=width,
        height=height,
        tools=tools,
        toolbar_location=toolbar_location,
        active_scroll=active_scroll,
        tooltips=tooltips,
    )

    marks = p.scatter(
        x,
        y,
        source=cds,
        marker=marker,
        size=marker_size,
        alpha=marker_alpha,
        **kwargs
    )

    p.axis.major_label_text_font_size = marker_label_font_size
    p.xaxis.axis_label_text_font_size = axis_label_font_size
    p.yaxis.axis_label_text_font_size = axis_label_font_size

    return p, marks, cds


