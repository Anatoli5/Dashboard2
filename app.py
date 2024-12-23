"""Main application entry point."""

import os
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from frontend.callbacks.chart import register_chart_callbacks
from frontend.callbacks.data import register_data_callbacks
from config.settings import THEME, TICKER_LISTS

# Initialize the Dash app with Bootstrap dark theme
app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.DARKLY],
    suppress_callback_exceptions=True
)

# Configure the app
app.title = "Financial Dashboard"

# App layout
app.layout = html.Div([  # Wrapper div with fixed height
    dbc.Container([
        dbc.Row([
            # Sidebar
            dbc.Col([
                html.H4("Controls", className="mb-3"),
                
                # Category Dropdown
                html.Label("Add Category", className="mb-2"),
                dcc.Dropdown(
                    id='category-dropdown',
                    options=[{'label': cat, 'value': cat} for cat in TICKER_LISTS.keys()],
                    placeholder="Select a category to add tickers",
                    className="mb-3",
                    persistence=True,
                    persistence_type='local'
                ),
                
                # Ticker Multi-Select
                html.Label("Selected Tickers", className="mb-2"),
                dcc.Dropdown(
                    id='ticker-dropdown',
                    multi=True,
                    placeholder="Search and select tickers",
                    className="mb-3",
                    persistence=True,
                    persistence_type='local'
                ),
                
                # Interval Selection
                html.Label("Interval", className="mb-2"),
                dcc.Dropdown(
                    id='interval-dropdown',
                    options=[
                        {'label': '1 Day', 'value': '1d'},
                        {'label': '1 Week', 'value': '1wk'},
                        {'label': '1 Month', 'value': '1mo'}
                    ],
                    value='1d',
                    className="mb-3",
                    persistence=True,
                    persistence_type='local'
                ),
                
                # Date Range
                html.Label("Date Range", className="mb-2"),
                dcc.DatePickerRange(
                    id='date-range',
                    className="mb-3",
                    display_format='YYYY-MM-DD',
                    persistence=True,
                    persistence_type='local'
                ),
                
                # Log Scale Toggle
                dbc.Switch(
                    id='log-scale-switch',
                    label="Logarithmic Scale",
                    value=False,
                    className="mb-3",
                    persistence=True,
                    persistence_type='local'
                ),
                
                # Normalize Toggle
                dbc.Switch(
                    id='normalize-switch',
                    label="Normalize Prices",
                    value=False,
                    className="mb-3",
                    persistence=True,
                    persistence_type='local'
                ),
                
                # Update Button
                dbc.Button(
                    "Update Data",
                    id='update-button',
                    color="primary",
                    className="w-100 mb-3"
                )
            ], width=3, className="bg-dark p-4 border-end", style={"height": "100vh", "overflow-y": "auto"}),
            
            # Main Content
            dbc.Col([
                # Chart container with fixed height
                html.Div([
                    # Loading overlay
                    dbc.Spinner(
                        html.Div(id="loading-chart"),
                        type="border",
                        color="primary",
                        spinner_style={
                            "position": "absolute",
                            "top": "50%",
                            "left": "50%",
                            "transform": "translate(-50%, -50%)",
                            "zIndex": "1000"
                        }
                    ),
                    # Chart
                    dcc.Graph(
                        id='price-chart',
                        style={"height": "calc(100vh - 2rem)"},  # Full height minus padding
                        config={
                            'scrollZoom': True,
                            'showTips': True,
                            'modeBarButtonsToAdd': ['drawline', 'drawopenpath', 'eraseshape'],
                            'modeBarButtonsToRemove': ['lasso2d', 'select2d'],
                            'displaylogo': False
                        }
                    )
                ], style={
                    "position": "relative",
                    "height": "calc(100vh - 2rem)",  # Full height minus padding
                    "margin": "1rem 0"
                })
            ], width=9, className="p-4", style={"height": "100vh", "overflow": "hidden"})
        ], style={"margin": "0", "height": "100vh"})
    ], fluid=True, style={"height": "100vh", "padding": "0"})
], style={"height": "100vh", "overflow": "hidden"})

# Register callbacks
register_chart_callbacks(app)
register_data_callbacks(app)

if __name__ == '__main__':
    # Get port from environment or use default
    port = int(os.environ.get('PORT', 8050))
    
    # Run the app
    app.run_server(debug=True, host='0.0.0.0', port=port)
