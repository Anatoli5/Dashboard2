from typing import Dict
import plotly.graph_objects as go
import pandas as pd
import streamlit as st


class ChartManager:
    @staticmethod
    def create_price_chart(
            data_normalized: Dict[str, pd.DataFrame],
            log_scale: bool = False
    ) -> go.Figure:
        fig = go.Figure()

        for ticker, ticker_df in data_normalized.items():
            if not ticker_df.empty:
                fig.add_trace(go.Scattergl(
                    x=ticker_df.index,
                    y=ticker_df['close'],
                    mode='lines',
                    name=ticker
                ))

        # Update layout with improved configuration
        fig.update_layout(
            title="Financial Data",
            xaxis_title="Date",
            yaxis_title="Price" + (" (normalized)" if st.session_state.get('norm_date') else ""),
            hovermode="x unified",
            template="plotly_dark",
            yaxis_type="log" if log_scale else "linear"
        )

        return fig

