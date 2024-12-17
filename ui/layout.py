# File: ui/layout.py
# Replace entire file with this code

import streamlit as st
import plotly.graph_objects as go
from streamlit_plotly_events import plotly_events
import pandas as pd


class DashboardLayout:
    @staticmethod
    def setup_page() -> None:
        st.set_page_config(layout="wide")

    @staticmethod
    def render_main_area(fig: go.Figure) -> None:
        # Use plotly_events instead of st.plotly_chart
        clicked_points = plotly_events(
            fig,
            click_event=True,
            hover_event=False,
            select_event=False,
            key="plot"
        )

        # Handle click events for normalization
        if clicked_points:
            event = clicked_points[0]
            clicked_date_str = event.get('x')
            try:
                clicked_date = pd.to_datetime(clicked_date_str)
                st.session_state['norm_date'] = clicked_date
                st.rerun()
            except Exception as error:
                st.error(f"Failed to parse clicked date: {error}")

        # Display normalization reference date if set
        if st.session_state.get('norm_date'):
            st.write("**Normalization Reference Date:**", st.session_state['norm_date'])
