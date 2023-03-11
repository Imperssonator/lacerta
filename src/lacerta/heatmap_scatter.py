import pandas as pd
import numpy as np
from bokeh.io import curdoc
from bokeh.palettes import PiYG11
from bokeh.models import (
    BasicTicker, ColorBar, LinearColorMapper, CustomJS, ColumnDataSource, TapTool, OpenURL
)
from bokeh.plotting import figure
from bokeh.layouts import row


def heatmap_scatter(
    data,
    hm_width=800,
    hm_height=800,
    scatter_width=400,
    theme="caliber",
):
    """
    Make an interactive correlation heatmap where you can
    click on a square and bring up the raw data scatter plot

    Will compute the correlation matrix automatically, only
    displaying results for continuous, numerical columns

    Parameters
    ----------
    data: DataFrame
        Raw data for correlation analysis
    hm_width: int
        target width of the heatmap plot in pixels
    hm_height: int
        target height of the heatmap plot in pixels
    scatter_width: int
        target width of the scatter plot in pixels. Scatter height
        will be calculated to get a square aspect ratio.
    
    Returns
    -------
    layout: Row
        Bokeh Row object (contains heatmap and scatter plots)
    """

    # Prepare data
    df_corr = pd.DataFrame(data.corr().stack(), columns=['coef']).reset_index()
    
    # Set up color map and plot size
    colors = list(reversed(PiYG11))
    mapper = LinearColorMapper(palette=colors, low=-1, high=1)
    headers = df_corr['level_0'].unique()

    # Build heatmap
    curdoc().theme = theme
    TOOLS_HM = "hover,save,tap,reset"
    cds_hm = ColumnDataSource(df_corr)

    p = figure(
        title="Correlation Heatmap",
        x_range=headers,
        y_range=list(reversed(headers)),
        x_axis_location="above",
        width=hm_width,
        height=hm_height,
        tools=TOOLS_HM,
        toolbar_location='below',
        tooltips=[
            ('x', '@level_0'),
            ('y', '@level_1'),
            ('Coef.', '@coef'),
        ]
    )

    p.grid.grid_line_color = None
    p.axis.axis_line_color = None
    p.axis.major_tick_line_color = None
    p.axis.major_label_text_font_size = "12px"
    p.axis.major_label_standoff = 0
    p.xaxis.major_label_orientation = np.pi / 3

    p.rect(
        x="level_0",
        y="level_1",
        width=0.95,
        height=0.95,
        source=cds_hm,
        fill_color={'field': 'coef', 'transform': mapper},
        line_color=None
    )

    color_bar = ColorBar(
        color_mapper=mapper,
        major_label_text_font_size="10px",
        ticker=BasicTicker(desired_num_ticks=len(colors)),
    #     formatter=PrintfTickFormatter(format="%d%.%d"),
        label_standoff=6,
        border_line_color=None
    )
    p.add_layout(color_bar, 'right')


    # Build scatterplot
    SCATTER_TOOLS = "hover,save,reset,wheel_zoom,pan"
    cds_scatter = ColumnDataSource(data)
    scatter_height = int(scatter_width * 1.43)

    p2 = figure(
        title=f"{headers[1]} vs. {headers[0]}",
        x_axis_label=headers[0],
        y_axis_label=headers[1],
        width=scatter_width,
        height=scatter_height,
        tools=SCATTER_TOOLS,
        toolbar_location='right',
        active_scroll='wheel_zoom',
        tooltips=[
            (hh, f'@{{{hh}}}') for hh in headers
            # (headers[0], f'@{headers[0]}'),
            # (headers[1], f'@{headers[1]}'),
        ],
    )
    p2_marks = p2.circle(
        headers[0],
        headers[1],
        source=cds_scatter,
        alpha=0.6,
        size=8,
    )
    p2.axis.major_label_text_font_size="8pt"
    p2.xaxis.axis_label_text_font_size = "10pt"
    p2.yaxis.axis_label_text_font_size = "10pt"

    # Build callback and apply to heatmap's taptool
    callback = CustomJS(
        args=dict(s=cds_hm, p2=p2, p2x=p2.xaxis[0], p2y=p2.yaxis[0], p2m=p2_marks),
        code="""
        const ind = s.selected.indices[s.selected.indices.length - 1]
        const newx = s.data.level_0[ind]
        const newy = s.data.level_1[ind]
        // console.log(ind)
        // console.log(newx, newy)
        // console.log(p2)
        // console.log(p2m.glyph.x.field, p2m.glyph.y.field)
        
        p2m.glyph.x.field = newx
        p2x.axis_label = newx
        p2m.glyph.y.field = newy
        p2y.axis_label = newy
        p2.title.text = newy + ' vs ' + newx
        p2m.glyph.change.emit()
        p2x.change.emit()
        p2y.change.emit()
        p2.change.emit()
        """
    )

    taptool = p.select(type=TapTool)
    taptool.callback = callback

    layout = row(p, p2)
    
    return layout
