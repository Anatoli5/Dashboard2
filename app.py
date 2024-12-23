"""Main application entry point."""

import os
from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
from frontend.callbacks.chart import register_chart_callbacks
from frontend.callbacks.data import register_data_callbacks
from frontend.callbacks.settings import register_settings_callbacks
from frontend.components.settings_modal import create_settings_modal
from config.settings import TICKER_LISTS

# Initialize the Dash app with Bootstrap dark theme
app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.DARKLY],
    suppress_callback_exceptions=True,
    update_title=None
)

# Configure the app
app.title = "Financial Dashboard"

# App layout
app.layout = html.Div([
    # Main layout
    dbc.Container([
        dbc.Row([
            # Sidebar
            dbc.Col([
                # Header with settings
                html.Div([
                    html.H4("Controls", className="mb-0"),
                    dbc.Button(
                        "⋮",  # Three dots menu icon
                        id="settings-open",
                        color="link",
                        className="p-0 ms-auto",
                        style={
                            "fontSize": "24px",
                            "textDecoration": "none",
                            "backgroundColor": "transparent",
                            "border": "none",
                            "boxShadow": "none",
                            "transition": "color 0.2s ease",
                            "cursor": "pointer"
                        }
                    )
                ], className="d-flex align-items-center mb-3"),
                
                # Category Dropdown
                html.Label("Add Category", className="mb-2"),
                dcc.Dropdown(
                    id='category-dropdown',
                    options=[{'label': cat, 'value': cat} for cat in TICKER_LISTS.keys()],
                    placeholder="Select a category to add tickers",
                    className="mb-3 dash-dropdown-dark",
                    persistence=True,
                    persistence_type='local'
                ),
                
                # Ticker Multi-Select
                html.Label("Selected Tickers", className="mb-2"),
                dcc.Dropdown(
                    id='ticker-dropdown',
                    multi=True,
                    placeholder="Search and select tickers",
                    className="mb-3 dash-dropdown-dark",
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
                    className="mb-3 dash-dropdown-dark",
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
            ], id="sidebar-container", width=3, className="p-4 border-end"),
            
            # Main Content
            dbc.Col([
                # Resizable container
                html.Div([
                    # Chart wrapper
                    html.Div([
                        # Chart
                        dcc.Graph(
                            id='price-chart',
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
                    ], id="chart-wrapper", style={
                        "height": "100%",
                        "width": "100%",
                        "padding": "1.5rem",
                        "borderRadius": "8px",
                        "boxShadow": "0 0 10px rgba(0,0,0,0.2)"
                    })
                ], id="chart-container", style={
                    "resize": "both",
                    "overflow": "hidden",
                    "minHeight": "400px",
                    "minWidth": "600px",
                    "height": "80vh",
                    "width": "100%",
                    "margin": "1rem",
                    "borderRadius": "10px",
                    "padding": "1px"
                })
            ], width=9, className="p-4")
        ], style={"margin": "0", "height": "100vh"})
    ], fluid=True, style={"height": "100vh", "padding": "0"}),
    
    # Settings modal
    create_settings_modal()
], id="main-container", style={"height": "100vh", "overflow": "hidden"})

# Register callbacks
register_chart_callbacks(app)
register_data_callbacks(app)
register_settings_callbacks(app)

# Add Font Awesome for icons
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

if __name__ == '__main__':
    # Get port from environment or use default
    port = int(os.environ.get('PORT', 8050))
    
    # Run the app
    app.run_server(debug=True, host='0.0.0.0', port=port)
