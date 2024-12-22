# File: ui/layout.py
# Replace entire file with this code

import streamlit as st
import plotly.graph_objects as go
from streamlit_plotly_events import plotly_events
import pandas as pd
from core.settings_manager import SettingsManager


class DashboardLayout:
    @staticmethod
    def apply_theme():
        """Apply theme-specific styles"""
        theme = SettingsManager.get_setting('theme', 'dark')
        
        if theme == "dark":
            st.markdown("""
                <style>
                    /* Main app */
                    section[data-testid="stSidebar"] {
                        background-color: #262730;
                        width: 300px;
                    }
                    .main > div {
                        background-color: #0E1117;
                    }
                    
                    /* Text colors */
                    .stMarkdown, .stText, p, h1, h2, h3 {
                        color: #FAFAFA !important;
                    }
                    
                    /* Inputs and controls */
                    .stTextInput > div > div > input,
                    .stNumberInput > div > div > input,
                    .stDateInput > div > div > input {
                        color: #FAFAFA;
                        background-color: #262730;
                        border-color: #4F4F4F;
                    }
                    
                    /* Select boxes */
                    .stSelectbox > div > div,
                    .stMultiSelect > div > div {
                        color: #FAFAFA;
                        background-color: #262730;
                        border-color: #4F4F4F;
                    }
                    
                    /* Buttons */
                    .stButton > button {
                        color: #FAFAFA;
                        background-color: #262730;
                        border: 1px solid #4F4F4F;
                    }
                    .stButton > button:hover {
                        border-color: #6F6F6F;
                        color: #FFFFFF;
                    }
                    
                    /* Tabs */
                    .stTabs [data-baseweb="tab-list"] {
                        gap: 2px;
                        background-color: #0E1117;
                    }
                    .stTabs [data-baseweb="tab"] {
                        background-color: #262730;
                        color: #FAFAFA;
                        border-radius: 4px 4px 0 0;
                        border: none;
                        padding: 10px 20px;
                    }
                    .stTabs [aria-selected="true"] {
                        background-color: #404040;
                    }
                    
                    /* Info/Warning messages */
                    .stAlert {
                        background-color: #262730;
                        color: #FAFAFA;
                        border: 1px solid #4F4F4F;
                    }
                    
                    /* Plotly chart container */
                    [data-testid="stPlotlyChart"] {
                        background-color: #0E1117;
                    }
                    
                    /* Plotly elements */
                    .js-plotly-plot .plotly .main-svg {
                        background-color: #0E1117 !important;
                    }
                    
                    .js-plotly-plot .plotly .modebar {
                        background-color: transparent !important;
                    }
                    
                    /* Chart container */
                    .element-container:has([data-testid="stPlotlyChart"]) {
                        background-color: #0E1117;
                    }
                    
                    /* Expander */
                    .streamlit-expanderHeader {
                        background-color: #262730 !important;
                        color: #FAFAFA !important;
                    }
                    .streamlit-expanderContent {
                        background-color: #262730 !important;
                        color: #FAFAFA !important;
                    }
                </style>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <style>
                    /* Main app */
                    section[data-testid="stSidebar"] {
                        background-color: #F0F2F6;
                        width: 300px;
                    }
                    .main > div {
                        background-color: #FFFFFF;
                    }
                    
                    /* Text colors */
                    .stMarkdown, .stText, p, h1, h2, h3 {
                        color: #262730 !important;
                    }
                    
                    /* Inputs and controls */
                    .stTextInput > div > div > input,
                    .stNumberInput > div > div > input,
                    .stDateInput > div > div > input {
                        color: #262730;
                        background-color: #FFFFFF;
                        border-color: #E0E0E0;
                    }
                    
                    /* Select boxes */
                    .stSelectbox > div > div,
                    .stMultiSelect > div > div {
                        color: #262730;
                        background-color: #FFFFFF;
                        border-color: #E0E0E0;
                    }
                    
                    /* Buttons */
                    .stButton > button {
                        color: #262730;
                        background-color: #FFFFFF;
                        border: 1px solid #E0E0E0;
                    }
                    .stButton > button:hover {
                        border-color: #B0B0B0;
                        color: #000000;
                    }
                    
                    /* Tabs */
                    .stTabs [data-baseweb="tab-list"] {
                        gap: 2px;
                        background-color: #FFFFFF;
                    }
                    .stTabs [data-baseweb="tab"] {
                        background-color: #F0F2F6;
                        color: #262730;
                        border-radius: 4px 4px 0 0;
                        border: none;
                        padding: 10px 20px;
                    }
                    .stTabs [aria-selected="true"] {
                        background-color: #E0E0E0;
                    }
                    
                    /* Info/Warning messages */
                    .stAlert {
                        background-color: #FFFFFF;
                        color: #262730;
                        border: 1px solid #E0E0E0;
                    }
                    
                    /* Plotly chart container */
                    [data-testid="stPlotlyChart"] {
                        background-color: #FFFFFF;
                    }
                    
                    /* Plotly elements */
                    .js-plotly-plot .plotly .main-svg {
                        background-color: #FFFFFF !important;
                    }
                    
                    .js-plotly-plot .plotly .modebar {
                        background-color: transparent !important;
                    }
                    
                    /* Chart container */
                    .element-container:has([data-testid="stPlotlyChart"]) {
                        background-color: #FFFFFF;
                    }
                    
                    /* Expander */
                    .streamlit-expanderHeader {
                        background-color: #F0F2F6 !important;
                        color: #262730 !important;
                    }
                    .streamlit-expanderContent {
                        background-color: #F0F2F6 !important;
                        color: #262730 !important;
                    }
                </style>
            """, unsafe_allow_html=True)

    @staticmethod
    def setup_page():
        """Setup page configuration and theme"""
        # Set dark theme as default
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
        
        # Force dark theme
        st.markdown("""
            <script>
                var observer = new MutationObserver(function(mutations) {
                    if (document.querySelector('iframe')) {
                        document.querySelector('iframe').setAttribute('data-theme', 'dark');
                        observer.disconnect();
                    }
                });
                
                observer.observe(document, {childList: true, subtree: true});
            </script>
            """, unsafe_allow_html=True)
        
        # Set theme in session state
        if 'theme' not in st.session_state:
            st.session_state.theme = 'dark'

    @staticmethod
    def render_main_area(fig: go.Figure) -> None:
        """Render the main chart area"""
        # Add container styling first
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
            </style>
        """, unsafe_allow_html=True)
        
        # Create a container for the chart
        with st.container():
            # Use plotly_events with proper sizing
            clicked_points = plotly_events(
                fig,
                click_event=True,
                hover_event=False,
                select_event=False,
                override_width="100%",
                override_height="600px",
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

