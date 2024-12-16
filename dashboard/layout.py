from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional
import streamlit as st


@dataclass
class UserInputs:
    selected_tickers: List[str]
    interval: str
    start_date: datetime
    end_date: datetime
    log_scale: bool
    refresh_data: bool
    norm_date: Optional[datetime] = None


def create_dashboard(ticker_choices: List[str], max_date_range_days: int) -> UserInputs:
    """Creates the dashboard layout and handles user interactions."""
    # Ticker selection with autocomplete
    selected_tickers = st.sidebar.multiselect(
        "Select Tickers",
        options=ticker_choices,
        default=[],
        help="Start typing to search for tickers."
    )

    # Interval selection
    interval = st.sidebar.selectbox("Interval", ["1d", "1wk", "1mo"])

    # Date range selection
    max_date = datetime.now()
    min_date = max_date - timedelta(days=max_date_range_days)
    start_date = st.sidebar.date_input(
        "Start Date",
        min_value=min_date,
        max_value=max_date,
        value=max_date - timedelta(days=365)
    )
    end_date = st.sidebar.date_input(
        "End Date",
        min_value=min_date,
        max_value=max_date,
        value=max_date
    )

    # Log scale option
    log_scale = st.sidebar.checkbox("Log Scale", False)

    # Update data button
    refresh_data = st.sidebar.button("Update Data")

    # Initialize session state variables
    if 'norm_date' not in st.session_state:
        st.session_state['norm_date'] = None

    norm_date = st.session_state['norm_date']

    return UserInputs(
        selected_tickers=selected_tickers,
        interval=interval,
        start_date=start_date,
        end_date=end_date,
        log_scale=log_scale,
        refresh_data=refresh_data,
        norm_date=norm_date
    )
