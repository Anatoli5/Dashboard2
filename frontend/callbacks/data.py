"""Data-related callbacks."""

from typing import Dict, List, Tuple
import pandas as pd
from dash import Dash, Input, Output, State, callback_context
from dash.exceptions import PreventUpdate

from backend.data.manager import DataManager


def register_data_callbacks(app: Dash) -> None:
    """Register data-related callbacks."""
    
    data_manager = DataManager()
    
    @app.callback(
        [
            Output('ticker-dropdown', 'options'),
            Output('error-message', 'children')
        ],
        [Input('ticker-dropdown', 'search_value')],
        [State('error-message', 'children')]
    )
    def update_ticker_options(
        search_value: str,
        current_error: str
    ) -> Tuple[List[Dict], str]:
        """Update ticker dropdown options based on search."""
        if not search_value:
            return [], current_error
            
        try:
            # For now, just validate the searched ticker
            # In a real app, you might want to search a predefined list
            # or use an API to search for tickers
            search_ticker = search_value.upper()
            valid = data_manager.validate_tickers([search_ticker])
            
            if valid.get(search_ticker):
                return [{'label': search_ticker, 'value': search_ticker}], ""
            return [], f"Invalid ticker: {search_ticker}"
            
        except Exception as e:
            print(f"Error validating ticker: {str(e)}")
            return [], f"Error validating ticker: {str(e)}"
    
    @app.callback(
        [
            Output('date-range', 'min_date_allowed'),
            Output('date-range', 'max_date_allowed'),
            Output('date-range', 'start_date'),
            Output('date-range', 'end_date')
        ],
        [Input('ticker-dropdown', 'value')]
    )
    def update_date_range(tickers: List[str]) -> tuple:
        """Update date range based on available data."""
        if not tickers:
            raise PreventUpdate
        
        try:
            from datetime import datetime, timedelta
            
            # For now, use a fixed date range
            # In a real app, you might want to query the database
            # to find the actual date range of available data
            end = datetime.now()
            start = end - timedelta(days=365)
            
            return start.date(), end.date(), start.date(), end.date()
            
        except Exception as e:
            print(f"Error updating date range: {str(e)}")
            raise PreventUpdate