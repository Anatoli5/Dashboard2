from typing import List, Tuple
from datetime import datetime, timedelta
import streamlit as st


class SidebarControls:
    @staticmethod
    def render_ticker_selection(
            ticker_choices: List[str],
            default_tickers: List[str]
    ) -> List[str]:
        st.sidebar.title("Controls")
        return st.sidebar.multiselect(
            "Select Tickers",
            options=ticker_choices,
            default=default_tickers
        )

    @staticmethod
    def render_date_controls() -> Tuple[datetime, datetime]:
        start_date = st.sidebar.date_input(
            "Start Date",
            datetime.now() - timedelta(days=365)
        )
        end_date = st.sidebar.date_input(
            "End Date",
            datetime.now()
        )
        return start_date, end_date

    @staticmethod
    def render_chart_controls() -> Tuple[str, bool]:
        interval = st.sidebar.selectbox(
            "Interval",
            ["1d", "1wk", "1mo"]
        )
        log_scale = st.sidebar.checkbox("Log Scale", False)
        return interval, log_scale
