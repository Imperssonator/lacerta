from lacerta.base import scatterplot

import pandas as pd
import numpy as np
from scipy.stats import pearsonr

from bokeh.io import curdoc
from bokeh.palettes import PiYG11
from bokeh.plotting import figure
from bokeh.layouts import row, column
from bokeh.models import (
    BasicTicker, ColorBar, LinearColorMapper, CustomJS, ColumnDataSource, TapTool, OpenURL
)


def calculate_correlations(
    df,
    exclude_self=False,
    exclude_dupe=False,
):
    """
    Calculate correlations between all columns in a dataframe

    Parameters
    ----------
    df: pd.DataFrame
    exclude_self: bool
        Default False. If True, will remove self-correlations
        (i.e. from one column to itself)
    exclude_dupe: bool
        Default False. If True, will remove duplicate column pairs
        (e.g. will return corr(colA, colB) but not corr(colB, colA))
        Will default to colA being the earlier column in the dataframe

    Returns
    -------
    results_df: pd.DataFrame
        Columns: col1, col2, coef, p_value, log_p_value
    """
    # Initialize an empty list to store the results
    results = []

    # Get all column pairs and calculate correlations
    for ii, col1 in enumerate(df.columns):
        for jj, col2 in enumerate(df.columns):
            if exclude_self and (col1 == col2):
                continue
            elif exclude_dupe and (jj < ii):
                continue
            else:
                coef, p_value = pearsonr(df[col1], df[col2])
                results.append({
                    'col1': col1,
                    'col2': col2,
                    'coef': coef,
                    'p_value': p_value
                    })

    # Convert results to a DataFrame
    result_df = pd.DataFrame(results)
    result_df['log_p_value'] = -np.log10(result_df['p_value'])
    
    return result_df


def correlation_heatmap_scatter(
    data,
    hm_width=800,
    hm_height=800,
    scatter_height=400,
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

    # Calculate correlations
    df_corr = calculate_correlations(data)

    # Build heatmap
    TOOLS_HM = "hover,save,tap,reset"
    cds_hm = ColumnDataSource(df_corr)

    # Set up color map and plot size
    colors = list(reversed(PiYG11))
    mapper = LinearColorMapper(palette=colors, low=-1, high=1)
    headers = df_corr['col1'].unique()
    
    # Make the figure at least 800 pix but no more than 2000
    hm_width = min(max(800, len(data.columns) * 20), 2000)
    hm_height = hm_width

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
            ('x', '@col1'),
            ('y', '@col2'),
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
        x="col1",
        y="col2",
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


    # Build scatterplot figure
    scatter_width = int(1.43 * scatter_height)
    p2, p2_marks, p2_cds = scatterplot(
        data,
        headers[0],
        headers[1],
        width=scatter_width,
        height=scatter_height,
        title=f"{headers[1]} vs. {headers[0]}",
    )

    # Build callback and apply to heatmap's taptool
    callback = CustomJS(
        args=dict(s=cds_hm, p2=p2, p2x=p2.xaxis[0], p2y=p2.yaxis[0], p2m=p2_marks),
        code="""
        const ind = s.selected.indices[s.selected.indices.length - 1]
        const newx = s.data.col1[ind]
        const newy = s.data.col2[ind]
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

    layout = column(p, p2)
    
    return layout


def volcano_scatter(
    data,
    volc_width=600,
    volc_height=600,
    scatter_width=400,
):
    """
    Make an interactive volcano plot where you can
    click on a marker and bring up the raw data scatter plot

    Will compute the correlation matrix automatically, only
    displaying results for continuous, numerical columns

    Parameters
    ----------
    data: DataFrame
        Raw data for correlation analysis
    volc_width: int
        target width of the volcano plot in pixels
    volc_height: int
        target height of the volcano plot in pixels
    scatter_width: int
        target width of the scatter plot in pixels. Scatter height
        will be calculated to get a square aspect ratio.
    
    Returns
    -------
    layout: Row
        Bokeh Row object (contains heatmap and scatter plots)
    """

    # Calculate correlations
    df_corr = calculate_correlations(data, exclude_self=True, exclude_dupe=True)
    headers = df_corr['col1'].unique()
    
    # Set up color map and plot size
    colors = list(reversed(PiYG11))
    color_mapper = LinearColorMapper(palette=colors, low=-1, high=1)

    # Alpha values based on p-value (scaled between 0.6 and 1.0)
    df_corr["fill_alpha"] = np.interp(
        df_corr["log_p_value"],
        (df_corr["log_p_value"].min(), df_corr["log_p_value"].max()),
        (0.6, 1.0)
        )

    # Build volcano plot
    TOOLS_VOLC = "hover,save,tap,reset,wheel_zoom,pan"
    p, marks, cds_volc = scatterplot(
        df_corr,
        "coef",
        "log_p_value",
        x_label="Correlation Coefficient",
        y_label="-log(p-value)",
        title="Volcano Plot",
        width=volc_width,
        height=volc_height,
        tools=TOOLS_VOLC,
        toolbar_location="above",
        marker_alpha="fill_alpha",
        line_color="gray",
        fill_color={'field': 'coef', 'transform': color_mapper},
    )

    # Add a color bar for the correlation coefficient
    color_bar = ColorBar(
        color_mapper=color_mapper,
        label_standoff=12,
        location=(0, 0),
        title="Correlation Coefficient"
        )
    p.add_layout(color_bar, 'right')


    # Build scatterplot figure
    scatter_height = int(scatter_width)
    p2, p2_marks, p2_cds = scatterplot(
        data,
        headers[0],
        headers[1],
        width=scatter_width,
        height=scatter_height,
        title=f"{headers[1]} vs. {headers[0]}",
    )

    # Build callback and apply to heatmap's taptool
    callback = CustomJS(
        args=dict(s=cds_volc, p2=p2, p2x=p2.xaxis[0], p2y=p2.yaxis[0], p2m=p2_marks),
        code="""
        const ind = s.selected.indices[s.selected.indices.length - 1]
        const newx = s.data.col1[ind]
        const newy = s.data.col2[ind]
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
