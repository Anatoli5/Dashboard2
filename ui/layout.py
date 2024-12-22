# File: ui/layout.py
# Replace entire file with this code

import streamlit as st
import plotly.graph_objects as go
from streamlit_plotly_events import plotly_events
import pandas as pd
from core.settings_manager import SettingsManager


class DashboardLayout:
    """Handles the main layout of the dashboard"""
    
    @staticmethod
    def setup_page():
        """Setup the page configuration"""
        st.set_page_config(
            page_title="Financial Dashboard",
            page_icon="📈",
            layout="wide",
            initial_sidebar_state="expanded",
            menu_items={
                'Get Help': None,
                'Report a bug': None,
                'About': None
            }
        )
        
        # Apply base styling
        st.markdown("""
            <style>
                /* Main container */
                .main .block-container {
                    padding: 1rem;
                    max-width: 100%;
                }
                
                /* Chart container */
                .element-container:has([data-testid="stPlotlyChart"]) {
                    width: 100% !important;
                    margin: 0 !important;
                    padding: 0 !important;
                }
                
                /* Plotly chart wrapper */
                [data-testid="stPlotlyChart"] {
                    width: 100% !important;
                    padding: 0 !important;
                }
                
                /* Plotly elements */
                .js-plotly-plot {
                    width: 100% !important;
                }
                
                .js-plotly-plot .plot-container {
                    width: 100% !important;
                }
                
                /* Ensure dark theme */
                [data-testid="stPlotlyChart"] > div {
                    background-color: transparent !important;
                }
                
                .js-plotly-plot .plotly .main-svg {
                    background: transparent !important;
                }
                
                /* Mode bar */
                .js-plotly-plot .plotly .modebar {
                    background: transparent !important;
                }
                
                /* Remove any unwanted margins */
                .stPlotlyChart > div > div > div {
                    margin: 0 !important;
                }
                
                /* Fix z-index for sidebar controls */
                [data-testid="stSidebar"] {
                    z-index: 1000;
                }
                
                /* Ensure controls are clickable */
                .stCheckbox, .stSelectbox {
                    position: relative;
                    z-index: 1001;
                }
                
                /* Fix chart container z-index */
                .main .block-container [data-testid="stPlotlyChart"] {
                    z-index: 1;
                }
            </style>
        """, unsafe_allow_html=True)

    @staticmethod
    def render_main_area(fig) -> None:
        """Render the main chart area"""
        # Create a container for the chart
        with st.container():
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})

