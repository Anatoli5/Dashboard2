"""Chart component for displaying financial data."""

import dash_mantine_components as dmc
from dash import dcc

def create_chart():
    """Create a chart component with dark theme support."""
    return dmc.Paper(
        style={"height": "100%", "width": "100%"},
        children=[
            dcc.Graph(  # We keep dcc.Graph as dmc doesn't have a chart component
                id='chart',
                config={
                    'scrollZoom': True,
                    'showTips': True,
                    'modeBarButtonsToAdd': ['drawline', 'drawopenpath', 'eraseshape'],
                    'modeBarButtonsToRemove': ['lasso2d', 'select2d'],
                    'displaylogo': False,
                    'responsive': True
                },
                figure={
                    'layout': {
                        'template': 'plotly_dark',
                        'paper_bgcolor': 'rgba(0,0,0,0)',
                        'plot_bgcolor': 'rgba(0,0,0,0)',
                        'font': {'color': 'var(--mantine-color-default-0)'},
                        'xaxis': {
                            'gridcolor': 'var(--mantine-color-default-4)',
                            'linecolor': 'var(--mantine-color-default-4)',
                            'tickcolor': 'var(--mantine-color-default-4)',
                            'zerolinecolor': 'var(--mantine-color-default-4)'
                        },
                        'yaxis': {
                            'gridcolor': 'var(--mantine-color-default-4)',
                            'linecolor': 'var(--mantine-color-default-4)',
                            'tickcolor': 'var(--mantine-color-default-4)',
                            'zerolinecolor': 'var(--mantine-color-default-4)'
                        }
                    }
                },
                style={
                    "height": "100%",
                    "width": "100%"
                }
            )
        ]
    ) 