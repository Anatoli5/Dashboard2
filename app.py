"""Main application file."""

import os
import json
from dash import Dash, html, dcc
import dash_mantine_components as dmc
from frontend.components.settings_modal import create_settings_modal
from frontend.components.chart import create_chart
from frontend.callbacks.chart import register_chart_callbacks
from frontend.callbacks.data import register_data_callbacks
from frontend.callbacks.settings import register_settings_callbacks
from core.state_manager import StateManager
from config.settings import TICKER_LISTS

# Initialize the Dash app
app = Dash(
    __name__,
    suppress_callback_exceptions=True,
    update_title=None,
    use_pages=False,
    external_scripts=[
        {"src": "https://unpkg.com/react@18/umd/react.development.js"},
        {"src": "https://unpkg.com/react-dom@18/umd/react-dom.development.js"}
    ]
)

# Configure the app
app.title = "Financial Dashboard"

# Load saved state
app_state = StateManager.get_full_state()

# Create theme provider configuration for v0.12.1
theme = {
    'colorScheme': app_state.get('theme', 'dark'),
    'primaryColor': 'blue',
    'colors': {
        'dark': [
            '#C1C2C5',
            '#A6A7AB',
            '#909296',
            '#5C5F66',
            '#373A40',
            '#2C2E33',
            '#25262B',
            '#1A1B1E',
            '#141517',
            '#101113',
        ],
    },
    'components': {
        'Button': {'root': {'fontWeight': 500}},
        'Switch': {'root': {'cursor': 'pointer'}},
        'Select': {'input': {'cursor': 'pointer'}},
    }
}

app.layout = dmc.MantineProvider(
    theme=theme,
    inherit=True,
    withNormalizeCSS=True,
    withGlobalStyles=True,
    children=[
        html.Div(
            id="theme-provider",
            **{"data-theme": app_state.get('theme', 'dark')},
            style={'display': 'none'}
        ),
        dmc.Container(
            fluid=True,
            px=0,
            children=[
                # Main container
                dmc.Group(
                    spacing="md",
                    grow=True,
                    children=[
                        # Sidebar
                        dmc.Paper(
                            shadow="sm",
                            p="md",
                            withBorder=True,
                            style={"width": "280px"},
                            children=[
                                # Header with settings
                                dmc.Group(
                                    position="apart",
                                    mb="md",
                                    children=[
                                        dmc.Text("Controls", size="lg", fw=500),
                                        dmc.ActionIcon(
                                            id="settings-open",
                                            variant="subtle",
                                            size="lg",
                                            children="⚙️"
                                        )
                                    ]
                                ),
                                
                                # Category Dropdown
                                dmc.Select(
                                    id='category-dropdown',
                                    label="Add Category",
                                    placeholder="Select a category",
                                    data=[{'label': cat, 'value': cat} for cat in TICKER_LISTS.keys()],
                                    clearable=True,
                                    persistence=True,
                                    persistence_type='local',
                                    mb="md"
                                ),
                                
                                # Ticker Multi-Select
                                dmc.MultiSelect(
                                    id='ticker-dropdown',
                                    label="Selected Tickers",
                                    placeholder="Search and select tickers",
                                    clearable=True,
                                    searchable=True,
                                    persistence=True,
                                    persistence_type='local',
                                    mb="md"
                                ),
                                
                                # Interval Selection
                                dmc.Select(
                                    id='interval-dropdown',
                                    label="Interval",
                                    data=[
                                        {'label': 'Daily', 'value': '1d'},
                                        {'label': 'Weekly', 'value': '1wk'},
                                        {'label': 'Monthly', 'value': '1mo'}
                                    ],
                                    value='1d',
                                    persistence=True,
                                    persistence_type='local',
                                    mb="md"
                                ),
                                
                                # Date Range
                                dmc.Stack(
                                    spacing="sm",
                                    children=[
                                        dmc.DatePicker(
                                            id='date-range-start',
                                            label="Start Date",
                                            placeholder="Pick start date",
                                            value=app_state.get('start_date'),
                                            persistence=True,
                                            persistence_type='local',
                                            mb="md"
                                        ),
                                        dmc.DatePicker(
                                            id='date-range-end',
                                            label="End Date",
                                            placeholder="Pick end date",
                                            value=app_state.get('end_date'),
                                            persistence=True,
                                            persistence_type='local',
                                            mb="md"
                                        )
                                    ]
                                ),
                                
                                # Controls
                                dmc.Stack(
                                    spacing="sm",
                                    mb="md",
                                    children=[
                                        dmc.Group(
                                            position="apart",
                                            children=[
                                                dmc.Text("Log Scale"),
                                                dmc.Switch(
                                                    id='log-scale-switch',
                                                    checked=False,
                                                    persistence=True,
                                                    persistence_type='local'
                                                )
                                            ]
                                        ),
                                        dmc.Group(
                                            position="apart",
                                            children=[
                                                dmc.Text("Normalize"),
                                                dmc.Switch(
                                                    id='normalize-switch',
                                                    checked=False,
                                                    persistence=True,
                                                    persistence_type='local'
                                                )
                                            ]
                                        )
                                    ]
                                ),
                                
                                # Update Button
                                dmc.Button(
                                    "Update Data",
                                    id='update-button',
                                    variant="filled",
                                    fullWidth=True
                                )
                            ]
                        ),
                        
                        # Main content
                        dmc.Stack(
                            spacing="md",
                            style={"flex": 1},
                            children=[
                                # Chart container
                                dmc.Paper(
                                    shadow="sm",
                                    p="md",
                                    withBorder=True,
                                    children=create_chart()
                                ),
                                
                                # Info container
                                dmc.Paper(
                                    id='info-container',
                                    shadow="sm",
                                    p="md",
                                    withBorder=True,
                                    style={'height': '80px'}
                                )
                            ]
                        )
                    ]
                ),
                
                # Settings modal
                create_settings_modal()
            ]
        )
    ]
)

# Register callbacks
register_chart_callbacks(app)
register_data_callbacks(app)
register_settings_callbacks(app)

if __name__ == '__main__':
    # Get port from environment or use default
    port = int(os.environ.get('PORT', 8050))
    
    # Run the app
    app.run_server(debug=True, host='0.0.0.0', port=port)
