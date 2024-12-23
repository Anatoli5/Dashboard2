"""Settings-related callbacks."""

from typing import Dict, List
from dash import Dash, Input, Output, State, ALL
import dash_bootstrap_components as dbc
from core.state_manager import StateManager

def register_settings_callbacks(app: Dash) -> None:
    """Register settings-related callbacks."""
    
    @app.callback(
        Output("settings-modal", "is_open"),
        [Input("settings-open", "n_clicks")],
        [State("settings-modal", "is_open")],
    )
    def toggle_modal(n_open: int, is_open: bool) -> bool:
        """Toggle the settings modal."""
        if n_open:
            return not is_open
        return is_open 