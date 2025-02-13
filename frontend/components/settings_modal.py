"""Settings modal component."""

import dash_mantine_components as dmc

def create_settings_modal():
    """Create the settings modal."""
    return dmc.Modal(
        id="settings-modal",
        size="lg",
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
                    
                    # Color Scheme Breakdown
                    dmc.Stack(
                        spacing="xs",
                        children=[
                            dmc.Text("Color Scheme Breakdown:", fw=500),
                            dmc.Group(
                                spacing="xs",
                                children=[
                                    dmc.Paper(
                                        p="xs",
                                        withBorder=True,
                                        children=[
                                            dmc.Text("Text Colors:", size="sm", mb=5),
                                            dmc.Group(
                                                spacing="xs",
                                                children=[
                                                    dmc.Paper(
                                                        p="xs",
                                                        withBorder=True,
                                                        children=[
                                                            dmc.Text("Default [0]", size="xs", style={"color": "var(--mantine-color-dark-0)"}),
                                                            dmc.Text("Dimmed [1]", size="xs", style={"color": "var(--mantine-color-dark-1)"}),
                                                            dmc.Text("Secondary [2]", size="xs", style={"color": "var(--mantine-color-dark-2)"}),
                                                        ]
                                                    ),
                                                ]
                                            )
                                        ]
                                    ),
                                    dmc.Paper(
                                        p="xs",
                                        withBorder=True,
                                        children=[
                                            dmc.Text("Background Colors:", size="sm", mb=5),
                                            dmc.Group(
                                                spacing="xs",
                                                children=[
                                                    dmc.Paper(
                                                        p="xs",
                                                        withBorder=True,
                                                        children=[
                                                            dmc.Text("Paper [7]", size="xs", style={"backgroundColor": "var(--mantine-color-dark-7)", "padding": "5px"}),
                                                            dmc.Text("Background [6]", size="xs", style={"backgroundColor": "var(--mantine-color-dark-6)", "padding": "5px"}),
                                                            dmc.Text("Hover [5]", size="xs", style={"backgroundColor": "var(--mantine-color-dark-5)", "padding": "5px"}),
                                                        ]
                                                    ),
                                                ]
                                            )
                                        ]
                                    ),
                                    dmc.Paper(
                                        p="xs",
                                        withBorder=True,
                                        children=[
                                            dmc.Text("UI Elements:", size="sm", mb=5),
                                            dmc.Group(
                                                spacing="xs",
                                                children=[
                                                    dmc.Paper(
                                                        p="xs",
                                                        withBorder=True,
                                                        children=[
                                                            dmc.Text("Border [4]", size="xs", style={"borderColor": "var(--mantine-color-dark-4)", "borderWidth": "2px", "borderStyle": "solid", "padding": "5px"}),
                                                            dmc.Text("Muted [3]", size="xs", style={"color": "var(--mantine-color-dark-3)"}),
                                                        ]
                                                    ),
                                                ]
                                            )
                                        ]
                                    ),
                                ]
                            )
                        ]
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