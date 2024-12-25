"""Settings-related callbacks."""

import json
from typing import Dict, List
from dash import Dash, Input, Output, State, ctx
import dash_mantine_components as dmc
from core.state_manager import StateManager

def save_app_state(
    tickers: List[str] = None,
    interval: str = None,
    log_scale: bool = None,
    normalize: bool = None,
    start_date: str = None,
    end_date: str = None,
    norm_date: str = None,
    theme: str = None
) -> None:
    """Save application state to a file."""
    state = load_app_state()
    
    if tickers is not None:
        state['selected_tickers'] = tickers
    if interval is not None:
        state['interval'] = interval
    if log_scale is not None:
        state['log_scale'] = log_scale
    if normalize is not None:
        state['normalize'] = normalize
    if start_date is not None:
        state['start_date'] = start_date
    if end_date is not None:
        state['end_date'] = end_date
    if norm_date is not None:
        state['norm_date'] = norm_date
    if theme is not None:
        state['theme'] = theme
    
    # Save to file
    with open('app_state.json', 'w') as f:
        json.dump(state, f)

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
        Output("settings-modal", "opened"),
        [Input("settings-open", "n_clicks"), Input("settings-close", "n_clicks")],
        prevent_initial_call=True
    )
    def toggle_modal(open_clicks, close_clicks):
        """Toggle the settings modal."""
        triggered_id = ctx.triggered_id
        if triggered_id == 'settings-open':
            return True
        elif triggered_id == 'settings-close':
            return False
        return False

    @app.callback(
        Output("theme-select", "value"),
        Input("settings-modal", "opened"),
        prevent_initial_call=True
    )
    def load_theme_setting(opened):
        """Load the theme setting when modal opens."""
        if not opened:
            return None
        app_state = load_app_state()
        return app_state.get('theme', 'dark')

    @app.callback(
        Output("theme-select", "value", allow_duplicate=True),
        Input("theme-select", "value"),
        prevent_initial_call=True
    )
    def save_theme_setting(theme):
        """Save the theme setting when changed."""
        if theme is None:
            return 'dark'
        save_app_state(theme=theme)
        return theme 