"""Grid-related callbacks."""

from typing import Dict, List
import pandas as pd
from dash import Dash, Input, Output, State, callback_context

from backend.data.manager import DataManager
from core.state_manager import StateManager


def register_grid_callbacks(app: Dash) -> None:
    """Register grid-related callbacks."""
    
    data_manager = DataManager()
    
    @app.callback(
        Output('data-grid', 'rowData'),
        [
            Input('ticker-dropdown', 'value'),
            Input('interval-dropdown', 'value'),
            Input('update-button', 'n_clicks')
        ]
    )
    def update_grid_data(tickers: List[str], interval: str, n_clicks: int) -> List[Dict]:
        """Update the grid data."""
        if not tickers:
            return []
            
        try:
            # Update data if needed
            data_manager.update_ticker_data(tickers, interval)
            
            # Get the latest data point for each ticker
            latest_data = []
            for ticker in tickers:
                df = data_manager.load_data_for_tickers(
                    [ticker],
                    pd.Timestamp.now() - pd.Timedelta(days=2),
                    pd.Timestamp.now(),
                    interval
                ).get(ticker)
                
                if not df.empty:
                    latest = df.iloc[-1]
                    previous = df.iloc[-2] if len(df) > 1 else latest
                    
                    change = ((latest['close'] - previous['close']) / previous['close']) * 100
                    
                    latest_data.append({
                        'ticker': ticker,
                        'price': latest['close'],
                        'change': change,
                        'volume': latest['volume'],
                        'high': latest['high'],
                        'low': latest['low']
                    })
            
            return latest_data
            
        except Exception as e:
            print(f"Error updating grid data: {str(e)}")
            return [] 