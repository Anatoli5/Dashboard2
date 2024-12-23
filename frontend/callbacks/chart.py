"""Chart-related callbacks."""

from typing import Dict, List
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from dash import Dash, Input, Output, State, callback_context
import plotly.graph_objects as go
from dash.exceptions import PreventUpdate

from backend.data.manager import DataManager
from config.settings import THEME


def normalize_data(df: pd.DataFrame, click_point: Dict = None) -> pd.DataFrame:
    """Normalize data based on click point or start."""
    if df.empty:
        return df
        
    if click_point:
        # Find the closest point in time to the click
        click_time = pd.to_datetime(click_point['x'])
        idx = df.index.get_indexer([click_time], method='nearest')[0]
        reference_value = df.iloc[idx]
    else:
        reference_value = df.iloc[0]
        
    if reference_value == 0:
        return df
        
    return (df / reference_value) * 100


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
            Input('update-button', 'n_clicks'),
            Input('log-scale-switch', 'value'),
            Input('normalize-switch', 'value'),
            Input('price-chart', 'clickData')
        ],
        [State('price-chart', 'figure')]
    )
    def update_chart(
        tickers: List[str],
        interval: str,
        start_date: str,
        end_date: str,
        n_clicks: int,
        log_scale: bool,
        normalize: bool,
        click_data: Dict,
        current_figure: Dict
    ) -> Dict:
        """Update the price chart."""
        ctx = callback_context
        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None
        
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
            
            # Only update data if not triggered by click or switches
            if triggered_id not in ['price-chart', 'log-scale-switch', 'normalize-switch']:
                data_manager.update_ticker_data(tickers, interval)
            
            # Load data
            ticker_data = data_manager.load_data_for_tickers(
                tickers,
                start,
                end,
                interval
            )
            
            # Get click point for normalization
            click_point = None
            if normalize and click_data and triggered_id == 'price-chart':
                click_point = click_data['points'][0]
            
            # Create traces
            traces = []
            for ticker, df in ticker_data.items():
                if not df.empty:
                    # Get the close prices
                    close_prices = df['close']
                    
                    # Normalize if requested
                    if normalize:
                        close_prices = normalize_data(close_prices, click_point if click_point else None)
                    
                    traces.append(
                        go.Scatter(
                            x=df.index,
                            y=close_prices,
                            name=ticker,
                            mode='lines',
                            hovertemplate=(
                                f"{ticker}<br>"
                                "Date: %{x}<br>" +
                                ("Normalized: %{y:.1f}%<br>" if normalize else "Price: %{y:.2f}<br>") +
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
                    'title': {
                        'text': 'Normalized Price Chart (Click to change base point)' if normalize else 'Price Chart',
                        'x': 0.5,
                        'xanchor': 'center'
                    },
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
                        'title': 'Normalized Price (%)' if normalize else 'Price',
                        'showgrid': True,
                        'gridcolor': THEME['dark']['grid_color'],
                        'type': 'log' if log_scale else 'linear'
                    },
                    'paper_bgcolor': THEME['dark']['bg_color'],
                    'plot_bgcolor': THEME['dark']['plot_bg_color'],
                    'font': {'color': THEME['dark']['text_color']},
                    'hovermode': 'x unified',
                    'dragmode': 'zoom',
                    'modebar': {
                        'bgcolor': 'rgba(0,0,0,0)',
                        'color': THEME['dark']['text_color'],
                        'activecolor': THEME['dark']['text_color']
                    },
                    'annotations': [
                        {
                            'text': 'Click to normalize' if normalize else '',
                            'xref': 'paper',
                            'yref': 'paper',
                            'x': 0.5,
                            'y': 1.05,
                            'showarrow': False,
                            'font': {'size': 12, 'color': THEME['dark']['text_color']}
                        }
                    ] if normalize else []
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