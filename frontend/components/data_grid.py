"""Data grid component using AG Grid."""

from dash import html
import dash_ag_grid as dag
from config.themes import COLOR_SCHEMES

def create_data_grid(data=None, theme_name='dark'):
    """Create an AG Grid component with theme support."""
    
    # Default column definitions
    default_col_def = {
        "sortable": True,
        "filter": True,
        "resizable": True,
        "minWidth": 100,
        "cellStyle": {
            "color": COLOR_SCHEMES[theme_name]['text_primary']
        }
    }
    
    # Specific column definitions
    column_defs = [
        {
            "field": "ticker",
            "headerName": "Ticker",
            "pinned": "left",
            "width": 120
        },
        {
            "field": "price",
            "headerName": "Price",
            "type": "numericColumn",
            "valueFormatter": {"function": "d3.format(',.2f')(params.value)"},
            "width": 120
        },
        {
            "field": "change",
            "headerName": "Change %",
            "type": "numericColumn",
            "cellRenderer": "agAnimateShowChangeCellRenderer",
            "valueFormatter": {"function": "d3.format('+.2%')(params.value/100)"},
            "width": 120,
            "cellStyle": {
                "styleConditions": [
                    {
                        "condition": "params.value > 0",
                        "style": {"color": COLOR_SCHEMES[theme_name]['chart_colors'][2]}  # Green
                    },
                    {
                        "condition": "params.value < 0",
                        "style": {"color": COLOR_SCHEMES[theme_name]['chart_colors'][3]}  # Red
                    }
                ]
            }
        },
        {
            "field": "volume",
            "headerName": "Volume",
            "type": "numericColumn",
            "valueFormatter": {"function": "d3.format(',.0f')(params.value)"},
            "width": 140
        },
        {
            "field": "high",
            "headerName": "High",
            "type": "numericColumn",
            "valueFormatter": {"function": "d3.format(',.2f')(params.value)"},
            "width": 120
        },
        {
            "field": "low",
            "headerName": "Low",
            "type": "numericColumn",
            "valueFormatter": {"function": "d3.format(',.2f')(params.value)"},
            "width": 120
        }
    ]

    return html.Div([
        dag.AgGrid(
            id='data-grid',
            className='ag-theme-alpine-dark',
            columnDefs=column_defs,
            rowData=data or [],
            defaultColDef=default_col_def,
            dashGridOptions={
                "pagination": True,
                "paginationAutoPageSize": True,
                "animateRows": True,
                "enableCellChangeFlash": True,
                "rowSelection": "multiple",
                "enableRangeSelection": True,
                "enableCharts": True,
                "domLayout": 'autoHeight',
                "headerHeight": 40,
                "rowHeight": 32,
                "suppressMovableColumns": False,
                "suppressColumnMoveAnimation": True,
                "suppressRowHoverHighlight": False,
                "suppressCellSelection": False
            },
            style={
                "height": "100%",
                "width": "100%",
                "background": COLOR_SCHEMES[theme_name]['chart_inner_bg']
            }
        )
    ], style={
        "height": "calc(100vh - 200px)",
        "width": "100%",
        "padding": "1rem",
        "background": COLOR_SCHEMES[theme_name]['chart_outer_bg'],
        "borderRadius": "0.5rem",
        "border": f"1px solid {COLOR_SCHEMES[theme_name]['border']}"
    }) 