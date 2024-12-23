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
app.layout = dbc.Container([
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
                className="mb-3"
            ),
            
            # Ticker Multi-Select
            html.Label("Selected Tickers", className="mb-2"),
            dcc.Dropdown(
                id='ticker-dropdown',
                multi=True,
                placeholder="Search and select tickers",
                className="mb-3"
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
                className="mb-3"
            ),
            
            # Date Range
            html.Label("Date Range", className="mb-2"),
            dcc.DatePickerRange(
                id='date-range',
                className="mb-3",
                display_format='YYYY-MM-DD'
            ),
            
            # Log Scale Toggle
            dbc.Switch(
                id='log-scale-switch',
                label="Logarithmic Scale",
                value=False,
                className="mb-3"
            ),
            
            # Normalize Toggle
            dbc.Switch(
                id='normalize-switch',
                label="Normalize Prices",
                value=False,
                className="mb-3"
            ),
            
            # Update Button
            dbc.Button(
                "Update Data",
                id='update-button',
                color="primary",
                className="w-100 mb-3"
            )
        ], width=3, className="bg-dark p-4 border-end"),
        
        # Main Content
        dbc.Col([
            dcc.Graph(
                id='price-chart',
                className="h-100",
                config={
                    'scrollZoom': True,
                    'showTips': True,
                    'modeBarButtonsToAdd': ['drawline', 'drawopenpath', 'eraseshape'],
                    'modeBarButtonsToRemove': ['lasso2d', 'select2d'],
                    'displaylogo': False
                }
            )
        ], width=9, className="p-4")
    ], className="h-100")
], fluid=True, className="vh-100 bg-dark text-light p-0")

# Register callbacks
register_chart_callbacks(app)
register_data_callbacks(app)

if __name__ == '__main__':
    # Get port from environment or use default
    port = int(os.environ.get('PORT', 8050))
    
    # Run the app
    app.run_server(debug=True, host='0.0.0.0', port=port)
