"""Settings-related callbacks."""

import json
from typing import Dict, List
from dash import Dash, Input, Output, State, ALL
import dash_bootstrap_components as dbc
from core.state_manager import StateManager
from dash import callback_context

def save_app_state(app_state):
    """Save app state to file."""
    try:
        with open('app_state.json', 'w') as f:
            json.dump(app_state, f, indent=4)
    except Exception as e:
        print(f"Error saving app state: {e}")

def load_app_state():
    """Load app state from file."""
    try:
        with open('app_state.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading app state: {e}")
        return {}

def register_settings_callbacks(app: Dash) -> None:
    """Register settings-related callbacks."""
    
    @app.callback(
        Output("settings-modal", "is_open"),
        [Input("settings-open", "n_clicks"), Input("settings-close", "n_clicks")],
        [State("settings-modal", "is_open")],
    )
    def toggle_modal(n1, n2, is_open):
        """Toggle the settings modal."""
        if n1 or n2:
            return not is_open
        return is_open

    @app.callback(
        [Output("theme-stylesheet", "href"),
         Output("theme-selector", "value")],
        Input("theme-selector", "value"),
        State("theme-selector", "value")
    )
    def update_theme(new_theme, current_theme):
        """Update the theme and persist the selection."""
        if not new_theme:
            return dbc.themes.DARKLY, dbc.themes.DARKLY
            
        # Save theme to app state
        try:
            app_state = load_app_state()
            app_state['theme'] = new_theme  # Save the full theme URL
            save_app_state(app_state)
        except Exception as e:
            print(f"Error saving theme: {e}")
            
        return new_theme, new_theme 