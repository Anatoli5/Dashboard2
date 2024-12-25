"""Chart component for displaying financial data."""

from dash import dcc, html

def create_chart():
    """Create a chart component with dark theme support."""
    return html.Div([
        dcc.Graph(
            id='chart',
            config={
                'scrollZoom': True,
                'showTips': True,
                'modeBarButtonsToAdd': ['drawline', 'drawopenpath', 'eraseshape'],
                'modeBarButtonsToRemove': ['lasso2d', 'select2d'],
                'displaylogo': False
            },
            style={
                "height": "100%",
                "width": "100%"
            }
        )
    ], style={
        "height": "100%",
        "width": "100%"
    }) 