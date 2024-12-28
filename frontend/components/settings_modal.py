"""Settings modal component."""

import dash_mantine_components as dmc

def create_settings_modal():
    """Create the settings modal."""
    return dmc.Modal(
        id="settings-modal",
        size="md",
        children=[
            dmc.Stack(
                spacing="md",
                children=[
                    dmc.Text("Settings", size="lg", fw=500),
                    
                    # Theme Selection
                    dmc.Select(
                        id="theme-select",
                        label="Theme",
                        data=[
                            {"value": "dark", "label": "Dark Mode"},
                            {"value": "light", "label": "Light Mode"}
                        ],
                        value="dark",
                        clearable=False
                    ),
                    
                    # Close Button
                    dmc.Group(
                        position="right",
                        children=[
                            dmc.Button(
                                "Close",
                                id="settings-close",
                                variant="outline"
                            )
                        ]
                    )
                ]
            )
        ]
    ) 