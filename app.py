# File: app.py

import streamlit as st
from datetime import datetime, timedelta
from config.loader import ConfigLoader
from config.settings import Settings
from core.data_manager import DatabaseManager
from core.utils import normalize_data, adjust_range_and_interval
from core.state_manager import StateManager
from ui.layout import DashboardLayout
from ui.sidebar import SidebarControls
from visualization.charts import ChartManager

def initialize_session_state():
    """Initialize default session state values if not already set"""
    if 'initialized' not in st.session_state:
        default_values = {
            'initialized': True,
            'norm_date': None,
            'start_date': (datetime.now() - timedelta(days=365)).date(),
            'end_date': datetime.now().date(),
            'interval': '1d',
            'log_scale': False,
            'selected_tickers': [],
            'data_provider': 'yahoo'  # Default data provider
        }

        for key, value in default_values.items():
            if key not in st.session_state:
                st.session_state[key] = value

def main():
    try:
        DashboardLayout.setup_page()
        initialize_session_state()

        # Data Provider Selection in Sidebar
        st.sidebar.title("Data Provider Settings")
        provider = st.sidebar.selectbox(
            "Select Data Provider",
            ["Yahoo Finance", "Alpha Vantage"],
            index=0 if st.session_state['data_provider'] == 'yahoo' else 1
        )
        
        # Alpha Vantage API Key input if selected
        api_key = None
        if provider == "Alpha Vantage":
            api_key = st.sidebar.text_input(
                "Alpha Vantage API Key",
                type="password",
                help="Enter your Alpha Vantage API key. Get one at https://www.alphavantage.co/support/#api-key"
            )
            if not api_key:
                st.sidebar.warning("Please enter an Alpha Vantage API key to use this provider")
                return

        # Update provider in session state
        st.session_state['data_provider'] = 'yahoo' if provider == "Yahoo Finance" else 'alpha_vantage'

        # Initialize database manager with selected provider
        if 'db_manager' not in st.session_state or st.session_state.get('current_provider') != provider:
            st.session_state.db_manager = DatabaseManager(
                data_provider=st.session_state['data_provider'],
                api_key=api_key
            )
            st.session_state['current_provider'] = provider
        
        db_manager = st.session_state.db_manager
        state_loaded = StateManager.load_state()
        
        tickers_df = ConfigLoader.load_tickers(Settings.TICKERS_FILE)
        ticker_choices = tickers_df['ticker'].tolist()
        default_tickers = st.session_state['selected_tickers'] if state_loaded else (
            ["BTC-USD", "ETH-USD"] if all(t in ticker_choices for t in ["BTC-USD", "ETH-USD"])
            else ticker_choices[:2]
        )

        selected_tickers = SidebarControls.render_ticker_selection(
            ticker_choices,
            default_tickers
        )
        st.session_state['selected_tickers'] = selected_tickers

        start_date = SidebarControls.render_date_input(
            "Start Date",
            st.session_state['start_date']
        )
        end_date = SidebarControls.render_date_input(
            "End Date",
            st.session_state['end_date']
        )

        interval, log_scale = SidebarControls.render_chart_controls(
            default_interval=st.session_state['interval'],
            default_log_scale=st.session_state['log_scale']
        )

        st.session_state.update({
            'start_date': start_date,
            'end_date': end_date,
            'interval': interval,
            'log_scale': log_scale
        })

        interval = adjust_range_and_interval(start_date, end_date, interval)
        st.info("Click on any point in the chart to normalize all curves to that date.")

        try:
            db_manager.update_ticker_data(selected_tickers, interval=interval)
            data_loaded = db_manager.load_data_for_tickers(
                selected_tickers,
                start_date,
                end_date,
                interval=interval
            )

            if not any(not df.empty for df in data_loaded.values()):
                st.warning("No data available for the selected tickers and time range.")
                return

            data_normalized = normalize_data(
                data_loaded,
                st.session_state.get('norm_date')
            )

            fig = ChartManager.create_price_chart(data_normalized, log_scale)
            DashboardLayout.render_main_area(fig)

        except Exception as e:
            st.error(f"Error processing data: {str(e)}")

    except Exception as e:
        st.error(f"Application error: {str(e)}")
    finally:
        StateManager.save_state()

if __name__ == "__main__":
    main()
