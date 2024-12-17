import streamlit as st
from datetime import datetime
from typing import List, Tuple


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
            default=default_tickers,
            key="ticker_selector"
        )

    @staticmethod
    def render_date_input(label: str, default_value: datetime) -> datetime:
        return st.sidebar.date_input(
            label,
            value=default_value
        )

    @staticmethod
    def render_chart_controls(
            default_interval: str = "1d",
            default_log_scale: bool = False
    ) -> Tuple[str, bool]:
        st.sidebar.subheader("Chart Settings")

        interval = st.sidebar.selectbox(
            "Interval",
            ["1d", "1wk", "1mo"],
            index=["1d", "1wk", "1mo"].index(default_interval)
        )

        log_scale = st.sidebar.checkbox(
            "Log Scale",
            value=default_log_scale
        )

        # Add normalization controls
        st.sidebar.subheader("Normalization")
        enable_norm = st.sidebar.checkbox("Enable Price Normalization")

        if enable_norm:
            norm_date = st.sidebar.date_input(
                "Normalization Date",
                value=st.session_state.get('norm_date') or st.session_state['start_date'],
                min_value=st.session_state['start_date'],
                max_value=st.session_state['end_date']
            )
            st.session_state['norm_date'] = norm_date
        else:
            st.session_state['norm_date'] = None

        return interval, log_scale
