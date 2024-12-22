# File: ui/layout.py
# Replace entire file with this code

import streamlit as st
import plotly.graph_objects as go
from streamlit_plotly_events import plotly_events
import pandas as pd
from core.settings_manager import SettingsManager
from core.chart_manager import ChartManager


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
            # Display the chart with Streamlit's native plotly_chart
            st.plotly_chart(
                fig,
                use_container_width=True,
                config=ChartManager.CHART_CONFIG
            )
            
            # Create an invisible events layer that matches the main chart
            events_fig = go.Figure(fig)  # Create a copy for events
            events_fig.update_layout(
                # Make it transparent but keep the same size
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                showlegend=False,
                margin=dict(l=0, r=0, t=0, b=0, pad=0),
                yaxis=dict(visible=False),
                xaxis=dict(visible=False),
                annotations=[],  # Remove any annotations
                height=600  # Match the main chart height
            )
            
            # Capture events with plotly_events
            clicked_points = plotly_events(
                events_fig,
                click_event=True,
                hover_event=False,
                select_event=False,
                key="plot_events",
                override_height=600,  # Match the main chart height
                override_width="100%"
            )
            
            if clicked_points:
                event = clicked_points[0]
                clicked_date_str = event.get('x')
                try:
                    clicked_date = pd.to_datetime(clicked_date_str)
                    if st.session_state.norm_date != clicked_date:
                        st.session_state.norm_date = clicked_date
                        st.session_state.needs_rerun = True
                        st.session_state.data_cache = {}  # Clear cache to ensure fresh normalization
                        st.rerun()
                except Exception as e:
                    st.error(f"Failed to parse clicked date: {e}")

            # Display normalization reference date if set
            norm_date = st.session_state.get('norm_date')
            if norm_date is not None:  # Check explicitly for None
                st.write("**Normalization Reference Date:**", norm_date.strftime('%Y-%m-%d'))

