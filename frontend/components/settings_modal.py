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
                            {"label": "Dark", "value": "dark"},
                            {"label": "Light", "value": "light"},
                            {"label": "Auto", "value": "auto"}
                        ],
                        value="dark",
                        persistence=True,
                        persistence_type='local'
                    ),
                    
                    # Color Palette
                    dmc.Text("Color Palette", size="sm", fw=500),
                    dmc.ColorPicker(
                        id="color-palette",
                        format="hex",
                        swatches=["#1c7ed6", "#37b24d", "#f59f00", "#e03131"],
                        swatchesPerRow=7,
                        withPicker=True,
                        fullWidth=True
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