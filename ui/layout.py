import streamlit as st
import plotly.graph_objects as go


class DashboardLayout:
    @staticmethod
    def setup_page() -> None:
        st.set_page_config(layout="wide")

    @staticmethod
    def render_main_area(fig: go.Figure) -> None:
        st.plotly_chart(fig, use_container_width=True)
