"""Main application entry point."""

import os
import json
from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
from frontend.callbacks.chart import register_chart_callbacks
from frontend.callbacks.data import register_data_callbacks
from frontend.callbacks.settings import register_settings_callbacks
from frontend.components.settings_modal import create_settings_modal, THEMES, THEME_URLS
from config.settings import TICKER_LISTS, THEME
from core.state_manager import StateManager

# Initialize the Dash app
app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.DARKLY],
    suppress_callback_exceptions=True
)

# Create the app layout
app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.H1("Financial Dashboard", className="text-center mb-4")
        ])
    ]),
    
    # Main content
    dbc.Row([
        # Sidebar
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Controls", className="card-title"),
                    # Add Category
                    html.Div([
                        html.Label("Add Category"),
                        dbc.Select(
                            id="category-dropdown",
                            options=[
                                {"label": category, "value": category}
                                for category in TICKER_LISTS.keys()
                            ],
                            value="Crypto",
                            className="mb-3"
                        )
                    ]),
                    # Selected Tickers
                    html.Div([
                        html.Label("Selected Tickers"),
                        dcc.Dropdown(
                            id='ticker-dropdown',
                            multi=True,
                            className="mb-3 dash-dropdown-dark"
                        )
                    ]),
                    # Interval
                    html.Div([
                        html.Label("Interval"),
                        dbc.Select(
                            id='interval-dropdown',
                            options=[
                                {'label': '1 Day', 'value': '1d'},
                                {'label': '1 Week', 'value': '1wk'},
                                {'label': '1 Month', 'value': '1mo'}
                            ],
                            value='1d',
                            className="mb-3"
                        )
                    ]),
                    # Date Range
                    html.Div([
                        html.Label("Date Range"),
                        dcc.DatePickerRange(
                            id='date-range',
                            className="mb-3"
                        )
                    ]),
                    # Switches
                    html.Div([
                        dbc.Switch(
                            id="logarithmic-scale",
                            label="Logarithmic Scale",
                            value=False,
                            className="mb-2"
                        ),
                        dbc.Switch(
                            id="normalize-prices",
                            label="Normalize Prices",
                            value=False,
                            className="mb-3"
                        )
                    ]),
                    # Update Button
                    dbc.Button(
                        "Update Data",
                        id="update-button",
                        color="primary",
                        className="w-100 mb-3"
                    ),
                    # Settings Button
                    dbc.Button(
                        "Settings",
                        id="settings-open",
                        color="secondary",
                        className="w-100"
                    )
                ])
            ], style={
                "backgroundColor": THEME['bs-dark'],
                "borderRadius": "10px",
                "border": f"1px solid {THEME['border-color']}"
            })
        ], width=3),
        
        # Main content
        dbc.Col([
            # Chart container
            html.Div([
                dcc.Graph(
                    id='chart',
                    style={
                        "height": "100%",
                        "width": "100%"
                    },
                    config={
                        'scrollZoom': True,
                        'showTips': True,
                        'modeBarButtonsToAdd': ['drawline', 'drawopenpath', 'eraseshape'],
                        'modeBarButtonsToRemove': ['lasso2d', 'select2d'],
                        'displaylogo': False
                    }
                )
            ], id="chart-container", style={
                "position": "relative",
                "resize": "both",
                "overflow": "hidden",
                "minHeight": "400px",
                "minWidth": "600px",
                "height": "80vh",
                "width": "100%",
                "margin": "1rem",
                "padding": "1rem",
                "backgroundColor": THEME['bs-dark'],
                "borderRadius": "10px",
                "border": f"1px solid {THEME['border-color']}"
            })
        ], width=9)
    ], style={
        "margin": "0",
        "backgroundColor": THEME['bs-body-bg']
    }),
    
    # Settings modal
    create_settings_modal()
], fluid=True, style={
    "backgroundColor": THEME['bs-body-bg'],
    "minHeight": "100vh",
    "padding": "2rem"
})

# Register callbacks
register_chart_callbacks(app)
register_data_callbacks(app)
register_settings_callbacks(app)

if __name__ == '__main__':
    # Get port from environment or use default
    port = int(os.environ.get('PORT', 8050))
    
    # Run the app
    app.run_server(debug=True, host='localhost', port=port)
