"""Main Dash application."""

import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from config.settings import APP_CONFIG, THEME, TICKER_LISTS

# Initialize the Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.DARKLY],
    suppress_callback_exceptions=True,
    **APP_CONFIG
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
                    # Category selection
                    html.Label("Quick Add by Category"),
                    dcc.Dropdown(
                        id='category-dropdown',
                        options=[
                            {'label': category, 'value': category}
                            for category in TICKER_LISTS.keys()
                        ],
                        placeholder="Select a category",
                        className="mb-3"
                    ),
                    # Ticker selection
                    html.Label("Select Tickers"),
                    dcc.Dropdown(
                        id='ticker-dropdown',
                        multi=True,
                        placeholder="Search for tickers (e.g., AAPL)",
                        className="mb-3"
                    ),
                    # Interval selection
                    html.Label("Select Interval"),
                    dcc.Dropdown(
                        id='interval-dropdown',
                        options=[
                            {'label': 'Daily', 'value': '1d'},
                            {'label': 'Weekly', 'value': '1wk'},
                            {'label': 'Monthly', 'value': '1mo'}
                        ],
                        value='1d',
                        className="mb-3"
                    ),
                    # Date range
                    html.Label("Select Date Range"),
                    dcc.DatePickerRange(
                        id='date-range',
                        className="mb-3",
                        display_format='YYYY-MM-DD'
                    ),
                    # Update button
                    dbc.Button(
                        "Update Data",
                        id="update-button",
                        color="primary",
                        className="w-100 mb-3"
                    ),
                    # Error messages
                    html.Div(id='error-message', className="text-danger")
                ])
            ])
        ], width=3),
        
        # Main chart area
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    # Loading spinner for chart
                    dbc.Spinner(
                        dcc.Graph(
                            id='price-chart',
                            config={
                                'displayModeBar': True,
                                'scrollZoom': True,
                                'displaylogo': False
                            }
                        ),
                        color="primary",
                        type="border",
                        fullscreen=False
                    )
                ])
            ])
        ], width=9)
    ])
], fluid=True, className="p-4")

# Register callbacks
from frontend.callbacks import register_callbacks
register_callbacks(app)

if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
