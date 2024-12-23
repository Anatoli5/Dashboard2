"""Chart-related callbacks."""

from typing import Dict, List
from datetime import datetime, timedelta
import pandas as pd
from dash import Dash, Input, Output, State, callback_context
import plotly.graph_objects as go
from dash.exceptions import PreventUpdate

from backend.data.manager import DataManager
from config.settings import THEME


def register_chart_callbacks(app: Dash) -> None:
    """Register chart-related callbacks."""
    
    data_manager = DataManager()
    
    @app.callback(
        Output('price-chart', 'figure'),
        [
            Input('ticker-dropdown', 'value'),
            Input('interval-dropdown', 'value'),
            Input('date-range', 'start_date'),
            Input('date-range', 'end_date'),
            Input('update-button', 'n_clicks')
        ],
        [State('price-chart', 'figure')]
    )
    def update_chart(
        tickers: List[str],
        interval: str,
        start_date: str,
        end_date: str,
        n_clicks: int,
        current_figure: Dict
    ) -> Dict:
        """Update the price chart."""
        # Check if callback was triggered
        if not callback_context.triggered:
            raise PreventUpdate
            
        # Handle empty tickers
        if not tickers:
            return {
                'data': [],
                'layout': {
                    'title': 'Select tickers to display',
                    'showlegend': True,
                    'template': 'plotly_dark',
                    'height': 600,
                    'xaxis': {'showgrid': True},
                    'yaxis': {'showgrid': True},
                    'paper_bgcolor': THEME['dark']['bg_color'],
                    'plot_bgcolor': THEME['dark']['plot_bg_color']
                }
            }
        
        try:
            # Convert dates
            if not start_date or not end_date:
                end = datetime.now()
                start = end - timedelta(days=365)
            else:
                start = datetime.strptime(start_date, '%Y-%m-%d')
                end = datetime.strptime(end_date, '%Y-%m-%d')
            
            # Update data
            data_manager.update_ticker_data(tickers, interval)
            
            # Load data
            ticker_data = data_manager.load_data_for_tickers(
                tickers,
                start,
                end,
                interval
            )
            
            # Create traces
            traces = []
            for ticker, df in ticker_data.items():
                if not df.empty:
                    traces.append(
                        go.Scatter(
                            x=df.index,
                            y=df['close'],
                            name=ticker,
                            mode='lines',
                            hovertemplate=(
                                f"{ticker}<br>"
                                "Date: %{x}<br>"
                                "Close: %{y:.2f}<br>"
                                "<extra></extra>"
                            )
                        )
                    )
            
            if not traces:
                return {
                    'data': [],
                    'layout': {
                        'title': 'No data available for selected tickers',
                        'showlegend': True,
                        'template': 'plotly_dark',
                        'height': 600
                    }
                }
            
            # Create figure
            figure = {
                'data': traces,
                'layout': {
                    'title': 'Price Chart',
                    'showlegend': True,
                    'template': 'plotly_dark',
                    'height': 600,
                    'xaxis': {
                        'title': 'Date',
                        'rangeslider': {'visible': False},
                        'showgrid': True,
                        'gridcolor': THEME['dark']['grid_color']
                    },
                    'yaxis': {
                        'title': 'Price',
                        'showgrid': True,
                        'gridcolor': THEME['dark']['grid_color']
                    },
                    'paper_bgcolor': THEME['dark']['bg_color'],
                    'plot_bgcolor': THEME['dark']['plot_bg_color'],
                    'font': {'color': THEME['dark']['text_color']},
                    'hovermode': 'x unified'
                }
            }
            
            return figure
            
        except Exception as e:
            print(f"Error updating chart: {str(e)}")
            return current_figure or {
                'data': [],
                'layout': {
                    'title': f'Error: {str(e)}',
                    'showlegend': True,
                    'template': 'plotly_dark',
                    'height': 600
                }
            }