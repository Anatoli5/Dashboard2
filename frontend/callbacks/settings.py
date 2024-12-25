"""Settings-related callbacks."""

import json
from typing import Dict, List, Optional
from dash import Dash, Input, Output, State, ctx, no_update
import dash_mantine_components as dmc

def save_app_state(
    tickers: Optional[List[str]] = None,
    interval: Optional[str] = None,
    log_scale: Optional[bool] = None,
    normalize: Optional[bool] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    norm_date: Optional[str] = None,
    theme: Optional[str] = None
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
    
    with open('app_state.json', 'w') as f:
        json.dump(state, f)

def load_app_state() -> Dict:
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
        state = load_app_state()
        return state.get('theme', 'dark')

    @app.callback(
        [
            Output("theme-select", "value", allow_duplicate=True),
            Output(dmc.MantineProvider.ids.colorScheme, "value")
        ],
        Input("theme-select", "value"),
        prevent_initial_call=True
    )
    def save_theme_setting(theme):
        """Save the theme setting when changed."""
        if theme is None:
            return 'dark', 'dark'
        save_app_state(theme=theme)
        return theme, theme 