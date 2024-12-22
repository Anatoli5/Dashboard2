import streamlit as st
from datetime import datetime, timedelta
from core.settings_manager import SettingsManager
from core.ticker_manager import TickerManager
from core.symbol_search import SymbolSearch
from ui.ticker_lists import TickerListsUI


class SidebarControls:
    @staticmethod
    def render_sidebar() -> None:
        """Render the sidebar controls"""
        st.sidebar.title("Dashboard Controls")
        
        # Settings section
        with st.sidebar.expander("⚙️ Settings", expanded=False):
            # Theme selector
            current_theme = st.session_state.theme
            new_theme = st.selectbox(
                "Theme",
                options=['dark', 'light'],
                index=0 if current_theme == 'dark' else 1,
                key='theme_selector'
            )
            if new_theme != current_theme:
                SettingsManager.set_setting('theme', new_theme)
                st.session_state.theme = new_theme
                st.session_state.needs_rerun = True
            
            # Data provider selector
            current_provider = st.session_state.data_provider
            new_provider = st.selectbox(
                "Data Provider",
                options=['yahoo', 'alphavantage'],
                index=0 if current_provider == 'yahoo' else 1,
                key='provider_selector'
            )
            
            # API Key input for Alpha Vantage
            if new_provider == 'alphavantage':
                api_key = st.text_input(
                    "Alpha Vantage API Key",
                    value=SettingsManager.get_setting('alphavantage_api_key', ''),
                    type='password',
                    key='api_key_input'
                )
                if api_key:
                    SettingsManager.set_setting('alphavantage_api_key', api_key)
            
            if new_provider != current_provider:
                SettingsManager.set_setting('data_provider', new_provider)
                st.session_state.data_provider = new_provider
                st.session_state.needs_rerun = True
                st.session_state.data_cache = {}
                st.session_state.cached_interval = None
        
        st.sidebar.markdown("---")

        # Render ticker lists section
        TickerListsUI.render_ticker_lists_section()
        
        st.sidebar.markdown("---")

        # Date range selection
        st.sidebar.subheader("Date Range")
        
        # End date selection
        end_date = st.sidebar.date_input(
            "End Date",
            value=st.session_state.end_date,
            max_value=datetime.now().date(),
            key="end_date_input"
        )
        if end_date != st.session_state.end_date:
            st.session_state.end_date = end_date
            st.session_state.needs_rerun = True
            st.session_state.cached_interval = None
        
        # Start date selection
        start_date = st.sidebar.date_input(
            "Start Date",
            value=st.session_state.start_date,
            max_value=end_date,
            key="start_date_input"
        )
        if start_date != st.session_state.start_date:
            st.session_state.start_date = start_date
            st.session_state.needs_rerun = True
            st.session_state.cached_interval = None
        
        # Interval selection
        st.sidebar.subheader("Interval")
        interval = st.sidebar.selectbox(
            "Select Interval",
            options=['1d', '1wk', '1mo'],
            index=['1d', '1wk', '1mo'].index(st.session_state.interval),
            key="interval_selector"
        )
        if interval != st.session_state.interval:
            st.session_state.interval = interval
            st.session_state.needs_rerun = True
            st.session_state.cached_interval = None
        
        # Chart options
        st.sidebar.subheader("Chart Options")
        
        # Log scale checkbox
        log_scale = st.sidebar.checkbox(
            "Logarithmic Scale",
            value=st.session_state.log_scale,
            key="log_scale_checkbox"
        )
        if log_scale != st.session_state.log_scale:
            st.session_state.log_scale = log_scale
            st.session_state.needs_rerun = True
        
        # Clear normalization
        if st.session_state.get('norm_date') is not None:
            if st.sidebar.button("Clear Normalization"):
                st.session_state.norm_date = None
                st.session_state.needs_rerun = True
                st.session_state.data_cache = {}
            st.sidebar.info(
                "📌 Normalized to: " + 
                st.session_state.norm_date.strftime('%Y-%m-%d')
            )
