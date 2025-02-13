"""Settings-related callbacks."""

from typing import Dict, List, Optional
from dash import Dash, Input, Output, State, ctx, no_update
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
        [
            Output("theme-select", "value", allow_duplicate=True),
            Output("mantine-provider", "theme")
        ],
        Input("theme-select", "value"),
        State("mantine-provider", "theme"),
        prevent_initial_call=True
    )
    def save_theme_setting(theme, current_theme):
        """Save the theme setting and update provider theme."""
        if theme is None:
            theme = 'dark'
        StateManager.set_state('theme', theme)
        
        # Update theme while preserving other settings
        new_theme = current_theme.copy() if current_theme else {}
        new_theme['colorScheme'] = theme
        
        return theme, new_theme 