"""Chart-related callbacks."""

from typing import Dict, List
from dash import Dash, Input, Output, State
import plotly.graph_objects as go
from datetime import datetime
import pandas as pd
from core.state_manager import StateManager
from config.settings import THEME
from backend.data.manager import DataManager

# Custom color sequence for better visibility
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

def normalize_prices(df: pd.DataFrame, norm_date: datetime = None) -> pd.DataFrame:
    """
    Normalize prices to 100 at a specific date.
    
    Args:
        df (pd.DataFrame): DataFrame with price data
        norm_date (datetime, optional): Date to normalize to. If None, uses first date
        
    Returns:
        pd.DataFrame: Normalized DataFrame
    """
    if df.empty:
        return df
        
    # Use first date if no normalization date specified
    if norm_date is None:
        base_value = df['close'].iloc[0]
    else:
        # Convert to timestamp for comparison
        norm_date_ts = pd.Timestamp(norm_date)
        if norm_date_ts not in df.index:
            # If exact date not found, use nearest date
            nearest_date = min(df.index, key=lambda x: abs(x - norm_date_ts))
            print(f"Using nearest date {nearest_date.date()} for normalization")
            norm_date_ts = nearest_date
        base_value = df.loc[norm_date_ts, 'close']
    
    df = df.copy()
    df['close'] = (df['close'] / base_value) * 100
    return df

def register_chart_callbacks(app: Dash) -> None:
    """Register chart-related callbacks."""
    
    data_manager = DataManager()
    
    @app.callback(
        Output('chart', 'figure'),
        [
            Input('ticker-dropdown', 'value'),
            Input('interval-dropdown', 'value'),
            Input('logarithmic-scale', 'value'),
            Input('normalize-prices', 'value'),
            Input('date-range', 'start_date'),
            Input('date-range', 'end_date'),
            Input('chart', 'clickData')
        ]
    )
    def update_chart(
        tickers: List[str],
        interval: str,
        log_scale: bool,
        normalize: bool,
        start_date: str,
        end_date: str,
        click_data: Dict
    ) -> go.Figure:
        """Update chart based on user selections."""
        if not tickers:
            return go.Figure()
            
        # Save state
        state = StateManager.load_state()
        state.update({
            'interval': interval,
            'log_scale': log_scale,
            'normalize': normalize,
            'start_date': start_date,
            'end_date': end_date
        })
        
        # Update normalization date if chart was clicked
        if click_data and normalize:
            try:
                clicked_date = click_data['points'][0]['x']
                state['norm_date'] = clicked_date
                print(f"Setting normalization date to {clicked_date}")
            except Exception as e:
                print(f"Error processing click data: {str(e)}")
        
        StateManager.save_state(state)
        
        # Create empty figure with dark template
        fig = go.Figure()
        
        try:
            # Convert dates
            start = datetime.strptime(start_date, '%Y-%m-%d') if start_date else datetime.now()
            end = datetime.strptime(end_date, '%Y-%m-%d') if end_date else datetime.now()
            
            # Get normalization date from state or use start date
            norm_date = state.get('norm_date')
            if norm_date:
                try:
                    if isinstance(norm_date, str):
                        if 'T' in norm_date:
                            norm_date = datetime.strptime(norm_date, '%Y-%m-%dT%H:%M:%S')
                        else:
                            norm_date = datetime.strptime(norm_date, '%Y-%m-%d')
                except Exception as e:
                    print(f"Error parsing norm_date: {str(e)}")
                    norm_date = start
            
            # Update data
            data_manager.update_ticker_data(tickers, interval)
            
            # Load data
            data = data_manager.load_data_for_tickers(tickers, start, end, interval)
            
            # Add traces with custom colors using WebGL
            for i, (ticker, df) in enumerate(data.items()):
                if not df.empty:
                    try:
                        # Normalize if requested
                        if normalize:
                            df = normalize_prices(df, norm_date)
                        
                        color = COLORS[i % len(COLORS)]
                        fig.add_trace(go.Scattergl(  # Using Scattergl for better performance
                            x=df.index,
                            y=df['close'],
                            name=ticker,
                            mode='lines',
                            line=dict(
                                color=color,
                                width=2.5
                            ),
                            customdata=[[ticker]]*len(df),
                            hovertemplate="<b>%{customdata[0]}</b><br>" +
                                        "Date: %{x}<br>" +
                                        "Price: %{y:.2f}<extra></extra>"
                        ))
                    except Exception as e:
                        print(f"Error processing {ticker}: {str(e)}")
        except Exception as e:
            print(f"Error updating chart: {str(e)}")
        
        # Update layout with optimized settings
        fig.update_layout(
            template='plotly_dark',
            plot_bgcolor=THEME['chart-outer-bg'],
            paper_bgcolor=THEME['chart-inner-bg'],
            font=dict(
                family="Arial, sans-serif",
                size=12,
                color=THEME['bs-body-color']
            ),
            title=dict(
                text=f"Normalized Price Chart (Click to set base)" if normalize else "Price Chart",
                x=0.5,
                xanchor='center',
                font=dict(size=24, color=THEME['bs-body-color'])
            ),
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01,
                bgcolor='rgba(0,0,0,0)',
                bordercolor=THEME['border-color'],
                borderwidth=1,
                font=dict(color=THEME['bs-body-color'])
            ),
            margin=dict(l=10, r=10, t=50, b=10, pad=0),
            xaxis=dict(
                showgrid=True,
                gridcolor=THEME['chart-grid'],
                linecolor=THEME['border-color'],
                tickfont=dict(color=THEME['bs-body-color']),
                title=dict(
                    text='Date',
                    font=dict(size=14, color=THEME['bs-body-color'])
                ),
                rangeslider=dict(visible=False),
                showline=True,
                mirror=True,
                zeroline=False,
                showspikes=True,
                spikecolor=THEME['chart-grid'],
                spikethickness=1
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor=THEME['chart-grid'],
                linecolor=THEME['border-color'],
                tickfont=dict(color=THEME['bs-body-color']),
                title=dict(
                    text='Normalized Price (%)' if normalize else 'Price',
                    font=dict(size=14, color=THEME['bs-body-color'])
                ),
                type='log' if log_scale else 'linear',
                showline=True,
                mirror=True,
                zeroline=False,
                showspikes=True,
                spikecolor=THEME['chart-grid'],
                spikethickness=1
            ),
            hovermode='x unified',
            hoverlabel=dict(
                bgcolor=THEME['chart-outer-bg'],
                font=dict(color=THEME['bs-body-color']),
                bordercolor=THEME['border-color']
            ),
            height=600,
            dragmode='zoom',
            modebar=dict(
                bgcolor='rgba(0,0,0,0)',
                color=THEME['bs-body-color'],
                activecolor=THEME['bs-body-color']
            ),
            clickmode='event'  # Enable click events
        )
        
        # Add watermark if normalization is enabled but no point selected
        if normalize and not state.get('norm_date'):
            fig.add_annotation(
                text="Click to set normalization point",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(size=30, color='rgba(255, 255, 255, 0.1)'),
                textangle=0,
                opacity=0.1
            )
        
        return fig