from typing import Dict, Any
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

class ChartManager:
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

    # Chart configuration
    CHART_CONFIG = {
        'displayModeBar': True,
        'displaylogo': False,
        'modeBarButtonsToRemove': ['select2d', 'lasso2d'],
        'toImageButtonOptions': {
            'format': 'png',
            'filename': 'chart',
            'height': 600,
            'width': 1200,
            'scale': 2
        },
        'responsive': True,
        'scrollZoom': True,
        'doubleClick': 'reset+autosize',  # Reset zoom on double click
        'showTips': True,  # Show tips in the mode bar
        'modeBarButtonsToAdd': ['drawline', 'drawopenpath', 'eraseshape'],  # Add drawing tools
        'displayModeBar': 'hover'  # Only show mode bar on hover
    }

    @staticmethod
    def get_theme_colors(theme: str = 'dark') -> Dict[str, Any]:
        """Get theme-specific colors and styles"""
        if theme == 'dark':
            return {
                'bg_color': '#0E1117',        # Match Streamlit's dark theme
                'plot_bg_color': '#0E1117',   # Match plot with background
                'grid_color': '#333333',      # Darker grid
                'text_color': '#FAFAFA',      # Light text
                'axis_color': '#666666',      # Lighter axis
                'watermark_color': 'rgba(255, 255, 255, 0.1)',
                'line_color': '#444444',      # Line color for borders
                'hover_bg': 'rgba(14, 17, 23, 0.9)'  # Dark hover background
            }
        else:
            return {
                'bg_color': '#FFFFFF',
                'plot_bg_color': '#FFFFFF',
                'grid_color': '#E5E5E5',
                'text_color': '#262730',
                'axis_color': '#666666',
                'watermark_color': 'rgba(0, 0, 0, 0.1)',
                'line_color': '#B0B0B0',
                'hover_bg': 'rgba(255, 255, 255, 0.9)'
            }

    @staticmethod
    def create_price_chart(
            data_normalized: Dict[str, pd.DataFrame],
            log_scale: bool = False,
            theme: str = "dark"
    ) -> go.Figure:
        """Create price chart with theme support"""
        colors = ChartManager.get_theme_colors(theme)
        
        # Create figure with appropriate template
        fig = go.Figure()

        # Add traces with custom colors
        for i, (ticker, ticker_df) in enumerate(data_normalized.items()):
            if not ticker_df.empty:
                color = ChartManager.COLORS[i % len(ChartManager.COLORS)]
                fig.add_trace(go.Scatter(
                    x=ticker_df.index,
                    y=ticker_df['close'],
                    mode='lines',
                    name=ticker,
                    line=dict(
                        color=color,
                        width=2.5
                    ),
                    customdata=[[ticker]]*len(ticker_df),
                    hovertemplate="<b>%{customdata[0]}</b><br>" +
                                "Date: %{x}<br>" +
                                "Price: %{y:.2f}<extra></extra>"
                ))

        # Update layout with theme-specific configuration
        fig.update_layout(
            template='plotly_dark' if theme == 'dark' else 'plotly',
            plot_bgcolor=colors['plot_bg_color'],
            paper_bgcolor=colors['bg_color'],
            font=dict(
                family="Arial, sans-serif",
                size=12,
                color=colors['text_color']
            ),
            title=dict(
                text="Price Chart",
                x=0.5,
                xanchor='center',
                font=dict(size=24, color=colors['text_color'])
            ),
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01,
                bgcolor='rgba(0,0,0,0)',
                bordercolor=colors['line_color'],
                borderwidth=1,
                font=dict(color=colors['text_color'])
            ),
            margin=dict(l=10, r=10, t=50, b=10, pad=0),
            xaxis=dict(
                showgrid=True,
                gridcolor=colors['grid_color'],
                linecolor=colors['axis_color'],
                tickfont=dict(color=colors['text_color']),
                title=dict(
                    text='Date',
                    font=dict(size=14, color=colors['text_color'])
                ),
                rangeslider=dict(visible=False),
                showline=True,
                mirror=True,
                zeroline=False
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor=colors['grid_color'],
                linecolor=colors['axis_color'],
                tickfont=dict(color=colors['text_color']),
                title=dict(
                    text='Price',
                    font=dict(size=14, color=colors['text_color'])
                ),
                type='log' if log_scale else 'linear',
                showline=True,
                mirror=True,
                zeroline=False
            ),
            hovermode='x unified',
            hoverlabel=dict(
                bgcolor=colors['hover_bg'],
                font=dict(color=colors['text_color']),
                bordercolor=colors['line_color']
            ),
            height=600
        )

        # Add watermark
        if not st.session_state.get('norm_date'):
            fig.add_annotation(
                text="Click to normalize",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(size=30, color=colors['watermark_color']),
                textangle=0,
                opacity=0.1
            )

        return fig