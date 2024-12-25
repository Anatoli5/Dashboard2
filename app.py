"""Main application file."""

import os
import json
from dash import Dash, html, dcc
import dash_mantine_components as dmc
from frontend.components.data_grid import create_data_grid
from frontend.components.settings_modal import create_settings_modal
from frontend.components.chart import create_chart
from frontend.callbacks.chart import register_chart_callbacks
from frontend.callbacks.data import register_data_callbacks
from frontend.callbacks.grid import register_grid_callbacks
from frontend.callbacks.settings import register_settings_callbacks, load_app_state
from config.settings import TICKER_LISTS

# Load saved state
app_state = load_app_state()

# Initialize the Dash app
app = Dash(
    __name__,
    suppress_callback_exceptions=True,
    update_title=None
)

# Configure the app
app.title = "Financial Dashboard"

# Create theme provider
theme = {
    'colorScheme': app_state.get('theme', 'dark'),
    'primaryColor': 'blue',
    'components': {
        'Button': {'styles': {'root': {'fontWeight': 500}}},
        'Switch': {'styles': {'root': {'cursor': 'pointer'}}},
        'Select': {'styles': {'input': {'cursor': 'pointer'}}},
    }
}

app.layout = dmc.MantineProvider(
    theme=theme,
    withGlobalStyles=True,
    children=[
        dmc.Container(
            fluid=True,
            px=0,
            children=[
                # Main container
                dmc.SimpleGrid(
                    cols=2,
                    spacing="md",
                    children=[
                        # Sidebar
                        dmc.Paper(
                            shadow="sm",
                            radius="md",
                            p="md",
                            withBorder=True,
                            style={"width": "280px"},
                            children=[
                                # Header with settings
                                dmc.Group(
                                    justify="space-between",
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
                                        {'label': '1 Minute', 'value': '1min'},
                                        {'label': '5 Minutes', 'value': '5min'},
                                        {'label': '15 Minutes', 'value': '15min'},
                                        {'label': '30 Minutes', 'value': '30min'},
                                        {'label': '1 Hour', 'value': '1hour'},
                                        {'label': '4 Hours', 'value': '4hour'},
                                        {'label': 'Daily', 'value': '1day'}
                                    ],
                                    value='1min',
                                    persistence=True,
                                    persistence_type='local',
                                    mb="md"
                                ),
                                
                                # Date Range
                                dmc.Group(
                                    grow=True,
                                    children=[
                                        dmc.DatePickerInput(
                                            id='date-range-start',
                                            label="Start Date",
                                            placeholder="Pick start date",
                                            value=app_state.get('start_date'),
                                            persistence=True,
                                            persistence_type='local',
                                            mb="md"
                                        ),
                                        dmc.DatePickerInput(
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
                                    gap="sm",
                                    mb="md",
                                    children=[
                                        dmc.Group(
                                            justify="space-between",
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
                                            justify="space-between",
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
                            gap="md",
                            style={"flex": 1},
                            children=[
                                # Tabs for Chart and Grid
                                dmc.Tabs(
                                    id="view-tabs",
                                    value="chart",
                                    children=[
                                        dmc.TabsList([
                                            dmc.TabsTab("Chart", value="chart"),
                                            dmc.TabsTab("Grid", value="grid")
                                        ]),
                                        dmc.TabsPanel(
                                            value="chart",
                                            children=dmc.Paper(
                                                shadow="sm",
                                                radius="md",
                                                p="md",
                                                withBorder=True,
                                                children=create_chart()
                                            )
                                        ),
                                        dmc.TabsPanel(
                                            value="grid",
                                            children=dmc.Paper(
                                                shadow="sm",
                                                radius="md",
                                                p="md",
                                                withBorder=True,
                                                children=create_data_grid()
                                            )
                                        )
                                    ]
                                ),
                                
                                # Info container
                                dmc.Paper(
                                    id='info-container',
                                    shadow="sm",
                                    radius="md",
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
register_grid_callbacks(app)
register_settings_callbacks(app)

if __name__ == '__main__':
    # Get port from environment or use default
    port = int(os.environ.get('PORT', 8050))
    
    # Run the app
    app.run_server(debug=True, host='0.0.0.0', port=port)
