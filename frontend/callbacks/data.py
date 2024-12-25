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
            Output('date-range-start', 'minDate'),
            Output('date-range-start', 'maxDate'),
            Output('date-range-end', 'minDate'),
            Output('date-range-end', 'maxDate')
        ],
        [
            Input('interval-dropdown', 'value')
        ]
    )
    def update_date_range(interval):
        """Update the date range based on the selected interval."""
        if not interval:
            return no_update, no_update, no_update, no_update
        
        # Calculate min and max dates
        min_date = datetime.now() - timedelta(days=365)
        max_date = datetime.now()
        
        # Format dates as strings
        min_date_str = min_date.strftime('%Y-%m-%d')
        max_date_str = max_date.strftime('%Y-%m-%d')
        
        return min_date_str, max_date_str, min_date_str, max_date_str
    
    @app.callback(
        [
            Output('chart', 'figure', allow_duplicate=True),
            Output('data-grid', 'rowData', allow_duplicate=True),
            Output('info-container', 'children', allow_duplicate=True)
        ],
        [
            Input('update-button', 'n_clicks'),
            State('ticker-dropdown', 'value'),
            State('interval-dropdown', 'value'),
            State('date-range-start', 'value'),
            State('date-range-end', 'value'),
            State('log-scale-switch', 'checked'),
            State('normalize-switch', 'checked')
        ],
        prevent_initial_call=True
    )
    def update_data(n_clicks, tickers, interval, start_date, end_date, log_scale, normalize):
        """Update the chart and grid data."""
        if not n_clicks or not tickers or not interval:
            return no_update, no_update, no_update
        
        # ... rest of the function remains the same ...
    
    @app.callback(
        Output('loading-chart', 'children'),
        [
            Input('ticker-dropdown', 'value'),
            Input('interval-dropdown', 'value'),
            Input('update-button', 'n_clicks')
        ]
    )
    def show_loading(tickers: List[str], interval: str, n_clicks: int) -> str:
        """Show loading spinner when data is being fetched."""
        ctx = callback_context
        if not ctx.triggered:
            raise PreventUpdate
            
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if trigger_id in ['ticker-dropdown', 'interval-dropdown', 'update-button']:
            return "Loading..."
            
        return ""