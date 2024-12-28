"""Settings-related callbacks."""

from typing import Dict, List, Optional
from dash import Dash, Input, Output, State, ctx, no_update, clientside_callback
import dash_mantine_components as dmc
from core.state_manager import StateManager

def register_settings_callbacks(app: Dash) -> None:
    """Register settings-related callbacks."""
    
    @app.callback(
        Output("settings-modal", "opened"),
        [Input("settings-open", "n_clicks"), Input("settings-close", "n_clicks")],
        prevent_initial_call=True
    )
    def toggle_modal(open_clicks, close_clicks):
        """Toggle the settings modal."""
        if not ctx.triggered_id:
            return no_update
        return ctx.triggered_id == "settings-open"

    @app.callback(
        Output("theme-select", "value"),
        Input("settings-modal", "opened"),
        prevent_initial_call=True
    )
    def load_theme_setting(opened):
        """Load the theme setting when modal opens."""
        if not opened:
            return no_update
        return StateManager.get_state('theme', 'dark')

    @app.callback(
        Output("theme-select", "value", allow_duplicate=True),
        Input("theme-select", "value"),
        prevent_initial_call=True
    )
    def save_theme_setting(theme):
        """Save the theme setting."""
        if theme is None:
            theme = 'dark'
        StateManager.set_state('theme', theme)
        return theme

    # Client-side callback for theme switching
    clientside_callback(
        """
        function(theme) {
            if (!theme) return dash_clientside.no_update;
            document.documentElement.setAttribute('data-mantine-color-scheme', theme);
            return dash_clientside.no_update;
        }
        """,
        Output("theme-provider", "data-theme"),
        Input("theme-select", "value"),
        prevent_initial_call=True
    ) 