"""Main application file."""

import os
from dash import Dash
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
            '#C1C2C5',  # 0: Default text
            '#A6A7AB',  # 1: Dimmed text
            '#909296',  # 2: Secondary text
            '#5C5F66',  # 3: Muted text
            '#373A40',  # 4: Border
            '#2C2E33',  # 5: Dark background hover
            '#25262B',  # 6: Dark background
            '#1A1B1E',  # 7: Paper background
            '#141517',  # 8: Dark overlay
            '#101113',  # 9: Darkest background
        ],
        'light': [
            '#1A1B1E',  # 0: Default text
            '#2C2E33',  # 1: Dimmed text
            '#5C5F66',  # 2: Secondary text
            '#909296',  # 3: Muted text
            '#E9ECEF',  # 4: Border
            '#F1F3F5',  # 5: Light background hover
            '#F8F9FA',  # 6: Light background
            '#FFFFFF',  # 7: Paper background
            '#F8F9FA',  # 8: Light overlay
            '#FFFFFF',  # 9: Lightest background
        ]
    },
    'components': {
        'Select': {
            'styles': {
                'input': {
                    'backgroundColor': 'var(--mantine-color-default-6)',
                    'color': 'var(--mantine-color-default-0)',
                    'borderColor': 'var(--mantine-color-default-4)'
                },
                'dropdown': {
                    'backgroundColor': 'var(--mantine-color-default-6)',
                    'borderColor': 'var(--mantine-color-default-4)'
                },
                'item': {
                    'color': 'var(--mantine-color-default-0)',
                    '&[data-selected]': {
                        'backgroundColor': 'var(--mantine-color-default-5)',
                        'color': 'var(--mantine-color-default-0)'
                    },
                    '&[data-hovered]': {
                        'backgroundColor': 'var(--mantine-color-default-5)'
                    }
                },
                'label': {
                    'color': 'var(--mantine-color-default-0)'
                }
            }
        },
        'MultiSelect': {
            'styles': {
                'input': {
                    'backgroundColor': 'var(--mantine-color-default-6)',
                    'color': 'var(--mantine-color-default-0)',
                    'borderColor': 'var(--mantine-color-default-4)'
                },
                'dropdown': {
                    'backgroundColor': 'var(--mantine-color-default-6)',
                    'borderColor': 'var(--mantine-color-default-4)'
                },
                'item': {
                    'color': 'var(--mantine-color-default-0)',
                    '&[data-selected]': {
                        'backgroundColor': 'var(--mantine-color-default-5)',
                        'color': 'var(--mantine-color-default-0)'
                    },
                    '&[data-hovered]': {
                        'backgroundColor': 'var(--mantine-color-default-5)'
                    }
                },
                'label': {
                    'color': 'var(--mantine-color-default-0)'
                }
            }
        },
        'DatePicker': {
            'styles': {
                'input': {
                    'backgroundColor': 'var(--mantine-color-default-6)',
                    'color': 'var(--mantine-color-default-0)',
                    'borderColor': 'var(--mantine-color-default-4)'
                },
                'dropdown': {
                    'backgroundColor': 'var(--mantine-color-default-6)',
                    'borderColor': 'var(--mantine-color-default-4)'
                },
                'label': {
                    'color': 'var(--mantine-color-default-0)'
                }
            }
        },
        'Paper': {
            'styles': {
                'root': {
                    'backgroundColor': 'var(--mantine-color-default-6)',
                    'color': 'var(--mantine-color-default-0)',
                    'borderColor': 'var(--mantine-color-default-4)'
                }
            }
        },
        'Text': {
            'styles': {
                'root': {
                    'color': 'var(--mantine-color-default-0)'
                }
            }
        },
        'ActionIcon': {
            'styles': {
                'root': {
                    'color': 'var(--mantine-color-default-0)',
                    '&:hover': {
                        'backgroundColor': 'var(--mantine-color-default-5)'
                    }
                }
            }
        },
        'Switch': {
            'styles': {
                'root': {
                    'label': {
                        'color': 'var(--mantine-color-default-0)'
                    }
                },
                'track': {
                    'backgroundColor': 'var(--mantine-color-default-4)',
                    'borderColor': 'var(--mantine-color-default-4)'
                },
                'thumb': {
                    'backgroundColor': 'var(--mantine-color-default-0)'
                }
            }
        },
        'Button': {
            'styles': {
                'root': {
                    'backgroundColor': 'var(--mantine-color-blue-6)',
                    'color': 'var(--mantine-color-default-0)',
                    '&:hover': {
                        'backgroundColor': 'var(--mantine-color-blue-7)'
                    }
                }
            }
        },
        'Group': {
            'styles': {
                'root': {
                    'backgroundColor': 'transparent'
                }
            }
        },
        'Stack': {
            'styles': {
                'root': {
                    'backgroundColor': 'transparent'
                }
            }
        }
    }
}

app.layout = dmc.MantineProvider(
    theme=theme,
    inherit=True,
    withNormalizeCSS=True,
    withGlobalStyles=True,
    id="mantine-provider",
    children=[
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
                                    style={"height": "80px"}
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
