"""Settings modal component."""

import dash_mantine_components as dmc

def create_settings_modal():
    """Create the settings modal."""
    return dmc.Modal(
        id="settings-modal",
        size="md",
        children=[
            dmc.Stack(
                gap="md",
                children=[
                    dmc.Text("Settings", size="lg", fw=500),
                    
                    # Theme Selection
                    dmc.Select(
                        id="theme-select",
                        label="Theme",
                        data=[
                            {"value": "light", "label": "Light"},
                            {"value": "dark", "label": "Dark"},
                            {"value": "auto", "label": "Auto"}
                        ],
                        value="dark",
                        clearable=False
                    ),
                    
                    # Close Button
                    dmc.Group(
                        justify="right",
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