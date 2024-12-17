from typing import Dict
import plotly.graph_objects as go
import pandas as pd
from plotly.graph_objs import Figure


class ChartManager:
    @staticmethod
    def create_price_chart(
            data_normalized: Dict[str, pd.DataFrame],
            log_scale: bool = False
    ) -> go.Figure:
        fig: Figure = go.Figure()

        for ticker, ticker_df in data_normalized.items():
            if not ticker_df.empty:
                fig.add_trace(go.Scattergl(
                    x=ticker_df.index,
                    y=ticker_df['close'],
                    mode='lines',
                    name=ticker
                ))

        fig.update_layout(
            title="Financial Data",
            xaxis_title="Date",
            yaxis_title="Price",
            yaxis_type="log" if log_scale else "linear"
        )

        return fig
