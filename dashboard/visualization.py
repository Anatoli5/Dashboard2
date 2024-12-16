from typing import Dict, Any
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from streamlit_plotly_events import plotly_events
from utils.data_processor import DataProcessor


def process_and_visualize_data(
        data_loaded: Dict[str, pd.DataFrame],
        user_inputs: Any,
        data_processor: DataProcessor
) -> None:
    """Processes data and generates visualizations."""

    # Adjust interval based on date range
    interval = data_processor.adjust_range_and_interval(
        user_inputs.start_date, user_inputs.end_date, user_inputs.interval
    )

    # Apply normalization if a reference date is set
    if user_inputs.norm_date:
        data_normalized = data_processor.normalize_data(
            data_loaded, user_inputs.norm_date
        )
    else:
        data_normalized = data_loaded

    # Create Plotly figure
    fig = go.Figure()
    for ticker, ticker_df in data_normalized.items():
        if not ticker_df.empty:
            fig.add_trace(go.Scattergl(
                x=ticker_df.index,
                y=ticker_df['close'],
                mode='lines',
                name=ticker
            ))

    # Update layout
    fig.update_layout(
        title="Financial Data",
        xaxis_title="Date",
        yaxis_title="Price" + (" (Normalized)" if user_inputs.norm_date else ""),
        hovermode="x unified",
        template="plotly_dark"
    )

    # Apply log scale if selected
    if user_inputs.log_scale:
        fig.update_yaxes(type='log')

    # Display the plot and capture click events
    clicked_points = plotly_events(
        fig,
        click_event=True,
        hover_event=False,
        select_event=False,
        key="plot"
    )

    # Handle click events for normalization
    if clicked_points:
        handle_click_event(clicked_points)

    # Display normalization reference date
    if st.session_state['norm_date']:
        st.write(
            "**Normalization Reference Date:**",
            st.session_state['norm_date'].strftime('%Y-%m-%d')
        )


def handle_click_event(clicked_points: Any) -> None:
    """Handles click events on the plot."""
    event = clicked_points[0]
    clicked_date_str = event.get('x')
    try:
        clicked_date = pd.to_datetime(clicked_date_str)
        st.session_state['norm_date'] = clicked_date
        st.rerun()
    except Exception as e:
        st.error(f"Failed to parse clicked date: {e}")
