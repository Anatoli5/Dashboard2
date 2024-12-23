"""Data-related callbacks."""

from typing import Dict, List, Tuple
import pandas as pd
from dash import Dash, Input, Output, State, callback_context
from dash.exceptions import PreventUpdate

from backend.data.manager import DataManager
from config.settings import TICKER_LISTS


def register_data_callbacks(app: Dash) -> None:
    """Register data-related callbacks."""
    
    data_manager = DataManager()
    
    # Create a flat list of all tickers with their categories
    all_tickers = []
    for category, tickers in TICKER_LISTS.items():
        for ticker in tickers:
            all_tickers.append({
                'label': f"{ticker} ({category})",
                'value': ticker
            })
    
    @app.callback(
        Output('ticker-dropdown', 'value'),
        [Input('category-dropdown', 'value')],
        [State('ticker-dropdown', 'value')]
    )
    def update_selected_tickers(category: str, current_tickers: List[str]) -> List[str]:
        """Update selected tickers based on category selection."""
        if not category:
            raise PreventUpdate
            
        # Get tickers for selected category
        category_tickers = TICKER_LISTS[category]
        
        # Combine with current tickers, removing duplicates
        current_tickers = current_tickers or []
        return list(set(current_tickers + category_tickers))
    
    @app.callback(
        [
            Output('ticker-dropdown', 'options'),
            Output('date-range', 'min_date_allowed'),
            Output('date-range', 'max_date_allowed'),
            Output('date-range', 'start_date'),
            Output('date-range', 'end_date'),
            Output('error-message', 'children')
        ],
        [
            Input('ticker-dropdown', 'search_value'),
            Input('ticker-dropdown', 'value')
        ]
    )
    def update_data_controls(search_value: str, selected_tickers: List[str]) -> tuple:
        """Update data controls based on user input."""
        ctx = callback_context
        trigger_id = ctx.triggered[0]['prop_id'] if ctx.triggered else None
        
        # Initialize default values
        options = all_tickers
        error_msg = ""
        from datetime import datetime, timedelta
        end = datetime.now()
        start = end - timedelta(days=365)
        
        try:
            # Filter options based on search value
            if trigger_id == 'ticker-dropdown.search_value' and search_value:
                search_upper = search_value.upper()
                options = [
                    opt for opt in all_tickers
                    if search_upper in opt['value'].upper() or search_upper in opt['label'].upper()
                ]
            
            # Handle date range update
            if trigger_id == 'ticker-dropdown.value' and not selected_tickers:
                raise PreventUpdate
            
            return (
                options,
                start.date(),
                end.date(),
                start.date(),
                end.date(),
                error_msg
            )
            
        except Exception as e:
            print(f"Error in data controls: {str(e)}")
            return (
                options,
                start.date(),
                end.date(),
                start.date(),
                end.date(),
                f"Error: {str(e)}"
            )