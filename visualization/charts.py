from typing import Dict

import pandas as pd
import plotly.graph_objects as go


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

        # Determine if data is normalized by checking if values are around 100
        is_normalized = any(
            not df.empty and abs(df['close'].iloc[0] - 100) < 90
            for df in data_normalized.values()
        )

        fig.update_layout(
            title="Financial Data",
            xaxis_title="Date",
            yaxis_title="Normalized Price (%)" if is_normalized else "Price",
            yaxis_type="log" if log_scale else "linear"
        )

        return fig

