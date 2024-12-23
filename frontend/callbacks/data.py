"""Data-related callbacks."""

from typing import Dict, List, Tuple
import pandas as pd
from dash import Dash, Input, Output, State, callback_context
from dash.exceptions import PreventUpdate
from datetime import datetime, timedelta

from backend.data.manager import DataManager
from core.ticker_manager import TickerManager
from core.state_manager import StateManager


def register_data_callbacks(app: Dash) -> None:
    """Register data-related callbacks."""
    
    data_manager = DataManager()
    
    @app.callback(
        [
            Output('ticker-dropdown', 'value'),
            Output('ticker-dropdown', 'options')
        ],
        [
            Input('category-dropdown', 'value'),
            Input('ticker-dropdown', 'search_value')
        ],
        [
            State('ticker-dropdown', 'value')
        ]
    )
    def update_ticker_selection(
        category: str,
        search_value: str,
        current_tickers: List[str]
    ) -> Tuple[List[str], List[Dict]]:
        """Update ticker selection based on category or search."""
        ctx = callback_context
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None
        
        # Initialize ticker state
        TickerManager.initialize()
        current_tickers = current_tickers or TickerManager.get_selected_tickers()
        
        # Get all available tickers
        available_tickers = TickerManager.get_available_tickers()
        
        if trigger_id == 'category-dropdown' and category:
            # Add all tickers from selected category
            category_tickers = TickerManager.get_tickers_by_category(category)
            new_tickers = list(set(current_tickers + category_tickers))
            TickerManager.set_selected_tickers(new_tickers)
            return new_tickers, available_tickers
            
        elif trigger_id == 'ticker-dropdown' and search_value:
            # Filter available tickers based on search
            search_upper = search_value.upper()
            filtered_tickers = [
                ticker for ticker in available_tickers
                if search_upper in ticker['label'].upper()
            ]
            return current_tickers, filtered_tickers
            
        return current_tickers, available_tickers
    
    @app.callback(
        [
            Output('date-range', 'min_date_allowed'),
            Output('date-range', 'max_date_allowed'),
            Output('date-range', 'start_date'),
            Output('date-range', 'end_date'),
            Output('interval-dropdown', 'value'),
            Output('log-scale-switch', 'value'),
            Output('normalize-switch', 'value')
        ],
        [Input('ticker-dropdown', 'value')],
        [
            State('interval-dropdown', 'value'),
            State('log-scale-switch', 'value'),
            State('normalize-switch', 'value')
        ]
    )
    def update_controls(
        tickers: List[str],
        current_interval: str,
        current_log_scale: bool,
        current_normalize: bool
    ) -> tuple:
        """Update controls based on selected tickers and saved state."""
        if not tickers:
            raise PreventUpdate
        
        # Get saved state or use defaults
        state = StateManager.load_state()
        end = datetime.now()
        start = end - timedelta(days=365)
        
        interval = state.get('interval', current_interval or '1d')
        log_scale = state.get('log_scale', current_log_scale or False)
        normalize = state.get('normalize', current_normalize or False)
        
        # Try to get saved dates
        try:
            if state.get('start_date'):
                start = datetime.strptime(state['start_date'], '%Y-%m-%d')
            if state.get('end_date'):
                end = datetime.strptime(state['end_date'], '%Y-%m-%d')
        except:
            pass
        
        return (
            start.date(),
            end.date(),
            start.date(),
            end.date(),
            interval,
            log_scale,
            normalize
        )