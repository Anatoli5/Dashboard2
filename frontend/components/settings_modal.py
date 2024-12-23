"""Settings modal component."""

from dash import html, dcc
import dash_bootstrap_components as dbc

def create_settings_modal():
    """Create the settings modal."""
    return dbc.Modal([
        dbc.ModalHeader(
            dbc.ModalTitle("Settings"),
            close_button=True,
            className="border-0"
        ),
        dbc.ModalBody([
            # Settings content goes here
            html.Div([
                html.Label("Settings content will go here", className="mb-2 d-block"),
            ], className="mb-4"),
        ], className="px-4"),
    ], id="settings-modal", is_open=False, size="sm", className="theme-modal") 