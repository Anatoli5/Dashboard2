"""Settings-related callbacks."""

from dash import Input, Output, State, ctx
from dash.exceptions import PreventUpdate
from core.state_manager import StateManager

def register_settings_callbacks(app):
    """Register settings-related callbacks."""
    
    @app.callback(
        Output("settings-modal", "is_open"),
        [
            Input("settings-open", "n_clicks"),
            Input("settings-close", "n_clicks"),
            Input("theme-selector", "value")
        ],
        [State("settings-modal", "is_open")],
    )
    def toggle_settings_modal(open_clicks, close_clicks, theme, is_open):
        """Toggle the settings modal and update theme."""
        if not ctx.triggered:
            return is_open
        
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        
        if button_id == "settings-open":
            return not is_open
        elif button_id == "settings-close":
            return False
        elif button_id == "theme-selector" and theme:
            # Save theme selection
            try:
                state = StateManager.load_state()
                state['theme'] = theme
                StateManager.save_state(state)
            except Exception as e:
                print(f"Error saving theme: {e}")
            
            return is_open
        
        return is_open 