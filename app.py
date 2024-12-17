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
            'selected_tickers': []
        }

        # Only set values that aren't already in session_state
        for key, value in default_values.items():
            if key not in st.session_state:
                st.session_state[key] = value


def main():
    try:
        # Initialize layout and database
        DashboardLayout.setup_page()
        db_manager = DatabaseManager()
        initialize_session_state()

        # Try to load previous state
        state_loaded = StateManager.load_state()

        # Load configuration
        tickers_df = ConfigLoader.load_tickers(Settings.TICKERS_FILE)
        ticker_choices = tickers_df['ticker'].tolist()
        default_tickers = st.session_state['selected_tickers'] if state_loaded else (
            ["AAPL", "BTC-USD"] if all(t in ticker_choices for t in ["AAPL", "BTC-USD"])
            else ticker_choices[:2]
        )

        # Render sidebar controls with saved state values
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

        # Update session state
        st.session_state['start_date'] = start_date
        st.session_state['end_date'] = end_date
        st.session_state['interval'] = interval
        st.session_state['log_scale'] = log_scale

        # Process data
        interval = adjust_range_and_interval(start_date, end_date, interval)

        # Update ticker data using DatabaseManager
        try:
            db_manager.update_ticker_data(selected_tickers, interval=interval)
        except Exception as e:
            st.error(f"Error updating ticker data: {str(e)}")
            return

        # Load data using DatabaseManager
        try:
            data_loaded = db_manager.load_data_for_tickers(
                selected_tickers,
                start_date,
                end_date,
                interval=interval
            )
        except Exception as e:
            st.error(f"Error loading ticker data: {str(e)}")
            return

        # Check if we have data to display
        if not any(not df.empty for df in data_loaded.values()):
            st.warning("No data available for the selected tickers and time range.")
            return

        # Normalize and visualize data
        data_normalized = normalize_data(
            data_loaded,
            st.session_state['norm_date']
        )

        # Create and display chart
        try:
            fig = ChartManager.create_price_chart(data_normalized, log_scale)
            DashboardLayout.render_main_area(fig)
        except Exception as e:
            st.error(f"Error creating chart: {str(e)}")
            return

        # Save state before shutdown
        try:
            StateManager.save_state()
        except Exception as e:
            st.error(f"Error saving application state: {str(e)}")

    except Exception as e:
        st.error(f"Application error: {str(e)}")


if __name__ == "__main__":
    main()
