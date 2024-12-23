"""Settings-related callbacks."""

import json
from typing import Dict, List
from dash import Dash, Input, Output, State, ALL, ctx
import dash_bootstrap_components as dbc
from core.state_manager import StateManager

def save_app_state(app_state):
    """Save app state to file."""
    try:
        print("Saving app state:", app_state)
        with open('app_state.json', 'w') as f:
            json.dump(app_state, f, indent=4)
        print("App state saved successfully")
    except Exception as e:
        print(f"Error saving app state: {e}")

def load_app_state():
    """Load app state from file."""
    try:
        with open('app_state.json', 'r') as f:
            state = json.load(f)
            print("Loaded app state:", state)
            return state
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
        print("Theme callback triggered")
        print("New theme:", new_theme)
        print("Current theme:", current_theme)
        print("Triggered by:", ctx.triggered_id)
        
        # If this is an automatic trigger (not user action), keep current theme
        if not ctx.triggered_id:
            print("Automatic trigger - keeping current theme")
            app_state = load_app_state()
            saved_theme = app_state.get('theme')
            if saved_theme:
                return saved_theme, saved_theme
            return current_theme, current_theme
            
        if not new_theme:
            print("No theme selected, using default")
            return dbc.themes.DARKLY, dbc.themes.DARKLY
            
        # Only save if this is a user change
        if new_theme != current_theme:
            print("Theme changed by user, saving...")
            try:
                app_state = load_app_state()
                app_state['theme'] = new_theme
                save_app_state(app_state)
                print("Theme saved successfully:", new_theme)
            except Exception as e:
                print(f"Error saving theme: {e}")
            
        return new_theme, new_theme 