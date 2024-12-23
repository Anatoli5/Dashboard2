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
        Output('chart', 'figure'),
        [
            Input('ticker-dropdown', 'value'),
            Input('interval-dropdown', 'value'),
            Input('date-range', 'start_date'),
            Input('date-range', 'end_date'),
            Input('update-button', 'n_clicks'),
            Input('log-scale-switch', 'value'),
            Input('normalize-switch', 'value'),
            Input('chart', 'clickData')
        ],
        [State('chart', 'figure')]
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
        if triggered_id not in ['chart']:
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
                        'xanchor': 'center',
                        'font': {'color': THEME['text_primary']}
                    },
                    'showlegend': True,
                    'template': 'plotly_dark',
                    'xaxis': {'showgrid': True, 'gridcolor': THEME['grid']},
                    'yaxis': {'showgrid': True, 'gridcolor': THEME['grid']},
                    'paper_bgcolor': THEME['chart_outer_bg'],
                    'plot_bgcolor': THEME['chart_inner_bg'],
                    'font': {'color': THEME['text_primary']},
                    'annotations': [{
                        'text': 'Use the controls on the left to select tickers',
                        'xref': 'paper',
                        'yref': 'paper',
                        'x': 0.5,
                        'y': 0.5,
                        'showarrow': False,
                        'font': {'size': 16, 'color': THEME['text_primary']}
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
            if triggered_id not in ['chart', 'log-scale-switch', 'normalize-switch']:
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
            if normalize and click_data and triggered_id == 'chart':
                click_point = click_data['points'][0]
            
            # Create traces
            traces = []
            for i, (ticker, df) in enumerate(ticker_data.items()):
                if not df.empty:
                    color = THEME['chart_colors'][i % len(THEME['chart_colors'])]
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
                                bgcolor=THEME['hover_bg'],
                                bordercolor=color,
                                font=dict(
                                    color=THEME['text_primary'],
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
                                bgcolor=THEME['hover_bg'],
                                bordercolor=color,
                                font=dict(
                                    color=THEME['text_primary'],
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
                        'title': {
                            'text': 'No data available for selected tickers',
                            'x': 0.5,
                            'xanchor': 'center',
                            'font': {'color': THEME['text_primary']}
                        },
                        'showlegend': True,
                        'template': 'plotly_dark',
                        'xaxis': {
                            'title': 'Date',
                            'rangeslider': {'visible': False},
                            'showgrid': True,
                            'gridcolor': THEME['grid'],
                            'domain': [0, 1],
                            'color': THEME['text_primary']
                        },
                        'yaxis': {
                            'title': 'Normalized Price (%)' if normalize else 'Price',
                            'showgrid': True,
                            'gridcolor': THEME['grid'],
                            'type': 'log' if log_scale else 'linear',
                            'side': 'left',
                            'color': THEME['text_primary']
                        },
                        'yaxis2': {
                            'title': 'Volume',
                            'showgrid': False,
                            'side': 'right',
                            'overlaying': 'y',
                            'color': THEME['text_primary']
                        },
                        'paper_bgcolor': THEME['chart_outer_bg'],
                        'plot_bgcolor': THEME['chart_inner_bg'],
                        'font': {'color': THEME['text_primary']},
                        'hovermode': 'closest',
                        'hoverdistance': 50,
                        'hoverlabel': {
                            'bgcolor': THEME['hover_bg'],
                            'font': {'size': 13},
                            'align': 'right',
                            'namelength': -1
                        },
                        'dragmode': 'zoom',
                        'modebar': {
                            'bgcolor': 'rgba(0,0,0,0)',
                            'color': THEME['text_primary'],
                            'activecolor': THEME['text_primary']
                        },
                        'legend': {
                            'bgcolor': 'rgba(0,0,0,0)',
                            'font': {'color': THEME['text_primary']},
                            'bordercolor': THEME['border'],
                            'borderwidth': 1
                        },
                        'margin': {'l': 60, 'r': 60, 't': 50, 'b': 50}
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
                        'font': {'color': THEME['text_primary']}
                    },
                    'showlegend': True,
                    'template': 'plotly_dark',
                    'xaxis': {
                        'title': 'Date',
                        'rangeslider': {'visible': False},
                        'showgrid': True,
                        'gridcolor': THEME['grid'],
                        'domain': [0, 1],
                        'color': THEME['text_primary']
                    },
                    'yaxis': {
                        'title': 'Normalized Price (%)' if normalize else 'Price',
                        'showgrid': True,
                        'gridcolor': THEME['grid'],
                        'type': 'log' if log_scale else 'linear',
                        'side': 'left',
                        'color': THEME['text_primary']
                    },
                    'yaxis2': {
                        'title': 'Volume',
                        'showgrid': False,
                        'side': 'right',
                        'overlaying': 'y',
                        'color': THEME['text_primary']
                    },
                    'paper_bgcolor': THEME['chart_outer_bg'],
                    'plot_bgcolor': THEME['chart_inner_bg'],
                    'font': {'color': THEME['text_primary']},
                    'hovermode': 'closest',
                    'hoverdistance': 50,
                    'hoverlabel': {
                        'bgcolor': THEME['hover_bg'],
                        'font': {'size': 13},
                        'align': 'right',
                        'namelength': -1
                    },
                    'dragmode': 'zoom',
                    'modebar': {
                        'bgcolor': 'rgba(0,0,0,0)',
                        'color': THEME['text_primary'],
                        'activecolor': THEME['text_primary']
                    },
                    'legend': {
                        'bgcolor': 'rgba(0,0,0,0)',
                        'font': {'color': THEME['text_primary']},
                        'bordercolor': THEME['border'],
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
                    'title': {
                        'text': f'Error: {str(e)}',
                        'x': 0.5,
                        'xanchor': 'center',
                        'font': {'color': THEME['text_primary']}
                    },
                    'showlegend': True,
                    'template': 'plotly_dark',
                    'xaxis': {
                        'title': 'Date',
                        'rangeslider': {'visible': False},
                        'showgrid': True,
                        'gridcolor': THEME['grid'],
                        'domain': [0, 1],
                        'color': THEME['text_primary']
                    },
                    'yaxis': {
                        'title': 'Normalized Price (%)' if normalize else 'Price',
                        'showgrid': True,
                        'gridcolor': THEME['grid'],
                        'type': 'log' if log_scale else 'linear',
                        'side': 'left',
                        'color': THEME['text_primary']
                    },
                    'yaxis2': {
                        'title': 'Volume',
                        'showgrid': False,
                        'side': 'right',
                        'overlaying': 'y',
                        'color': THEME['text_primary']
                    },
                    'paper_bgcolor': THEME['chart_outer_bg'],
                    'plot_bgcolor': THEME['chart_inner_bg'],
                    'font': {'color': THEME['text_primary']},
                    'hovermode': 'closest',
                    'hoverdistance': 50,
                    'hoverlabel': {
                        'bgcolor': THEME['hover_bg'],
                        'font': {'size': 13},
                        'align': 'right',
                        'namelength': -1
                    },
                    'dragmode': 'zoom',
                    'modebar': {
                        'bgcolor': 'rgba(0,0,0,0)',
                        'color': THEME['text_primary'],
                        'activecolor': THEME['text_primary']
                    },
                    'legend': {
                        'bgcolor': 'rgba(0,0,0,0)',
                        'font': {'color': THEME['text_primary']},
                        'bordercolor': THEME['border'],
                        'borderwidth': 1
                    },
                    'margin': {'l': 60, 'r': 60, 't': 50, 'b': 50}
                }
            }