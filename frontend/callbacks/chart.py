"""Chart-related callbacks."""

from typing import Dict, List
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from dash import Dash, Input, Output, State, callback_context
import plotly.graph_objects as go
from dash.exceptions import PreventUpdate

from backend.data.manager import DataManager
from core.ticker_manager import TickerManager
from core.state_manager import StateManager
from config.settings import THEME


# Custom color sequence from original project
COLORS = [
    '#2E91E5',  # Blue
    '#E15F99',  # Pink
    '#1CA71C',  # Green
    '#FB0D0D',  # Red
    '#DA16FF',  # Purple
    '#B68100',  # Brown
    '#EB663B',  # Orange
    '#511CFB',  # Indigo
    '#00CED1',  # Dark Turquoise
    '#FFD700',  # Gold
]


def normalize_data(df: pd.DataFrame, click_point: Dict = None) -> pd.DataFrame:
    """Normalize data based on click point or start."""
    if df.empty:
        return df
        
    if click_point:
        # Find the closest point in time to the click
        click_time = pd.to_datetime(click_point['x'])
        idx = df.index.get_indexer([click_time], method='nearest')[0]
        reference_value = df.iloc[idx]
        # Save normalization point in state
        StateManager.set_state('norm_date', click_time.isoformat())
    else:
        # Try to get saved normalization point
        saved_norm_date = StateManager.get_state('norm_date')
        if saved_norm_date and saved_norm_date in df.index:
            reference_value = df.loc[saved_norm_date]
        else:
            reference_value = df.iloc[0]
            StateManager.set_state('norm_date', df.index[0].isoformat())
        
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
        
        # Save current settings to state
        if triggered_id not in ['price-chart']:
            StateManager.update_state({
                'interval': interval,
                'log_scale': log_scale,
                'normalize': normalize,
                'start_date': start_date,
                'end_date': end_date
            })
        
        # Handle empty tickers
        if not tickers:
            return {
                'data': [],
                'layout': {
                    'title': {
                        'text': 'Select tickers to display',
                        'x': 0.5,
                        'xanchor': 'center'
                    },
                    'showlegend': True,
                    'template': 'plotly_dark',
                    'height': 600,
                    'xaxis': {'showgrid': True},
                    'yaxis': {'showgrid': True},
                    'paper_bgcolor': THEME['dark']['bg_color'],
                    'plot_bgcolor': THEME['dark']['plot_bg_color'],
                    'font': {'color': THEME['dark']['text_color']},
                    'annotations': [{
                        'text': 'Use the controls on the left to select tickers',
                        'xref': 'paper',
                        'yref': 'paper',
                        'x': 0.5,
                        'y': 0.5,
                        'showarrow': False,
                        'font': {'size': 16, 'color': THEME['dark']['text_color']}
                    }]
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
            for i, (ticker, df) in enumerate(ticker_data.items()):
                if not df.empty:
                    color = COLORS[i % len(COLORS)]
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
                            line=dict(
                                color=color,
                                width=2
                            ),
                            hovertemplate=(
                                f"<b>{ticker}</b><br>" +
                                "%{x}<br>" +
                                ("Value: %{y:.1f}%<br>" if normalize else "Price: %{y:.2f}<br>") +
                                "<extra></extra>"
                            ),
                            hoverlabel=dict(
                                bgcolor='rgba(0, 0, 0, 0.5)',
                                bordercolor=color,
                                font=dict(
                                    color=color,
                                    size=13
                                )
                            )
                        )
                    )
                    
                    # Add volume bars
                    traces.append(
                        go.Bar(
                            x=df.index,
                            y=df['volume'],
                            name=f"{ticker} Volume",
                            yaxis='y2',
                            marker_color=color,
                            opacity=0.3,
                            hovertemplate=(
                                f"<b>{ticker} Volume</b><br>" +
                                "%{x}<br>" +
                                "Volume: %{y:,.0f}<br>" +
                                "<extra></extra>"
                            ),
                            hoverlabel=dict(
                                bgcolor='rgba(0, 0, 0, 0.5)',
                                bordercolor=color,
                                font=dict(
                                    color=color,
                                    size=13
                                )
                            ),
                            visible='legendonly'
                        )
                    )
            
            if not traces:
                return {
                    'data': [],
                    'layout': {
                        'title': 'No data available for selected tickers',
                        'showlegend': True,
                        'template': 'plotly_dark',
                        'height': 600,
                        'paper_bgcolor': THEME['dark']['bg_color'],
                        'plot_bgcolor': THEME['dark']['plot_bg_color'],
                        'font': {'color': THEME['dark']['text_color']}
                    }
                }
            
            # Create figure
            figure = {
                'data': traces,
                'layout': {
                    'title': {
                        'text': 'Normalized Price Chart (Click to change base point)' if normalize else 'Price Chart',
                        'x': 0.5,
                        'xanchor': 'center',
                        'font': {'color': THEME['dark']['text_color']}
                    },
                    'showlegend': True,
                    'template': 'plotly_dark',
                    'height': 600,
                    'xaxis': {
                        'title': 'Date',
                        'rangeslider': {'visible': False},
                        'showgrid': True,
                        'gridcolor': THEME['dark']['grid_color'],
                        'domain': [0, 1],
                        'color': THEME['dark']['text_color']
                    },
                    'yaxis': {
                        'title': 'Normalized Price (%)' if normalize else 'Price',
                        'showgrid': True,
                        'gridcolor': THEME['dark']['grid_color'],
                        'type': 'log' if log_scale else 'linear',
                        'side': 'left',
                        'color': THEME['dark']['text_color']
                    },
                    'yaxis2': {
                        'title': 'Volume',
                        'showgrid': False,
                        'side': 'right',
                        'overlaying': 'y',
                        'color': THEME['dark']['text_color']
                    },
                    'paper_bgcolor': THEME['dark']['bg_color'],
                    'plot_bgcolor': THEME['dark']['plot_bg_color'],
                    'font': {'color': THEME['dark']['text_color']},
                    'hovermode': 'closest',
                    'hoverdistance': 50,
                    'hoverlabel': {
                        'bgcolor': 'rgba(0, 0, 0, 0.5)',
                        'font': dict(
                            size=13
                        )
                    },
                    'dragmode': 'zoom',
                    'modebar': {
                        'bgcolor': 'rgba(0,0,0,0)',
                        'color': THEME['dark']['text_color'],
                        'activecolor': THEME['dark']['text_color']
                    },
                    'legend': {
                        'bgcolor': 'rgba(0,0,0,0)',
                        'font': {'color': THEME['dark']['text_color']},
                        'bordercolor': THEME['dark']['grid_color'],
                        'borderwidth': 1
                    },
                    'margin': {'l': 60, 'r': 60, 't': 50, 'b': 50}
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
                    'height': 600,
                    'paper_bgcolor': THEME['dark']['bg_color'],
                    'plot_bgcolor': THEME['dark']['plot_bg_color'],
                    'font': {'color': THEME['dark']['text_color']}
                }
            }