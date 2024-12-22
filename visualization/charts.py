from typing import Dict, Any
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
import plotly.express as px


class ChartManager:
    # Custom color sequence for better visibility
    COLORS = [
        '#2E91E5',  # Blue
        '#E15F99',  # Pink
        '#1CA71C',  # Green
        '#FB0D0D',  # Red
        '#DA16FF',  # Purple
        '#222A2A',  # Dark Gray
        '#B68100',  # Brown
        '#750D86',  # Dark Purple
        '#EB663B',  # Orange
        '#511CFB',  # Indigo
    ]

    @staticmethod
    def get_theme_colors(theme: str = 'dark') -> Dict[str, Any]:
        """Get theme-specific colors and styles"""
        if theme == 'dark':
            return {
                'bg_color': 'rgba(14, 17, 23, 0)',
                'plot_bg_color': 'rgba(38, 39, 48, 0)',
                'grid_color': '#2C2F38',
                'text_color': '#FAFAFA',
                'axis_color': '#FAFAFA',
                'watermark_color': 'rgba(255, 255, 255, 0.1)',
                'line_color': '#4F4F4F',
                'hover_bg': 'rgba(38, 39, 48, 0.8)'
            }
        else:
            return {
                'bg_color': 'rgba(255, 255, 255, 0)',
                'plot_bg_color': 'rgba(240, 242, 246, 0)',
                'grid_color': '#E5E5E5',
                'text_color': '#262730',
                'axis_color': '#262730',
                'watermark_color': 'rgba(0, 0, 0, 0.1)',
                'line_color': '#B0B0B0',
                'hover_bg': 'rgba(255, 255, 255, 0.8)'
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
        
        # Force template update before adding traces
        fig.update_layout(
            template='plotly_dark' if theme == 'dark' else 'plotly',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )

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
                    customdata=[[ticker]]*len(ticker_df),  # Add ticker info for hover
                    hovertemplate="<b>%{customdata[0]}</b><br>" +
                                "Date: %{x}<br>" +
                                "Price: %{y:.2f}<extra></extra>"
                ))

        # Update layout with theme-specific configuration
        fig.update_layout(
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
                zeroline=False,
                showspikes=True,
                spikecolor=colors['grid_color'],
                spikethickness=1
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
                zeroline=False,
                showspikes=True,
                spikecolor=colors['grid_color'],
                spikethickness=1
            ),
            hovermode='x unified',
            hoverlabel=dict(
                bgcolor=colors['hover_bg'],
                font=dict(color=colors['text_color']),
                bordercolor=colors['line_color']
            ),
            autosize=True,
            height=600,  # Fixed height
            width=None,  # Allow width to be responsive
            modebar=dict(
                bgcolor='rgba(0,0,0,0)',
                color=colors['text_color'],
                activecolor=colors['text_color']
            ),
            dragmode='pan'  # Enable pan by default
        )

        # Add watermark
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

