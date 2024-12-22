# File: app.py

import streamlit as st
from datetime import datetime, timedelta
from core.data_manager import DatabaseManager
from core.utils import normalize_data, adjust_range_and_interval
from core.state_manager import StateManager
from ui.layout import DashboardLayout
from ui.sidebar import SidebarControls
from visualization.charts import ChartManager
from core.settings_manager import SettingsManager, SettingsUI
from core.ticker_manager import TickerManager
from core.symbol_search import SymbolSearch
import tornado.websocket
import contextlib

@contextlib.contextmanager
def handle_websocket_disconnect():
    """Context manager to handle WebSocket disconnections gracefully"""
    try:
        yield
    except (tornado.websocket.WebSocketClosedError, tornado.iostream.StreamClosedError):
        # These errors occur when the client disconnects, we can safely ignore them
        pass
    except Exception as e:
        # Re-raise other exceptions
        raise e

def initialize_session_state():
    """Initialize default session state values if not already set"""
    if 'initialized' not in st.session_state:
        default_values = {
            'initialized': True,
            'norm_date': None,
            'start_date': (datetime.now() - timedelta(days=365)).date(),
            'end_date': datetime.now().date(),
            'interval': '1d',
            'log_scale': False
        }

        for key, value in default_values.items():
            if key not in st.session_state:
                st.session_state[key] = value

def main():
    with handle_websocket_disconnect():
        try:
            DashboardLayout.setup_page()
            initialize_session_state()
            SettingsManager.initialize_settings()
            TickerManager.initialize()

            # Render settings UI and get provider change status
            provider_changed = SettingsUI.render_settings_section()

            # Initialize database manager with current settings
            if 'db_manager' not in st.session_state or provider_changed:
                try:
                    st.session_state.db_manager = DatabaseManager(
                        data_provider=SettingsManager.get_setting('data_provider'),
                        api_key=SettingsManager.get_setting('alpha_vantage_key')
                    )
                except ValueError as e:
                    st.error(f"Error initializing data provider: {str(e)}")
                    return
            
            db_manager = st.session_state.db_manager
            
            # Render symbol search if using Alpha Vantage
            if SettingsManager.get_setting('data_provider') == 'alpha_vantage':
                SymbolSearch.render_symbol_search()
            
            # Render ticker selection
            selected_tickers = TickerManager.render_ticker_selection()
            
            # Date range selection
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
                # Get provider-specific tickers
                provider_tickers = TickerManager.get_provider_tickers()
                
                if provider_tickers:
                    db_manager.update_ticker_data(provider_tickers, interval=interval)
                    data_loaded = db_manager.load_data_for_tickers(
                        provider_tickers,
                        start_date,
                        end_date,
                        interval=interval
                    )

                    if not any(not df.empty for df in data_loaded.values()):
                        st.warning("No data available for the selected tickers and time range.")
                        return

                    # Map the data back to display tickers
                    display_data = {
                        ticker: data_loaded[TickerManager.get_provider_ticker(ticker)]
                        for ticker in selected_tickers
                        if TickerManager.get_provider_ticker(ticker) in data_loaded
                    }

                    data_normalized = normalize_data(
                        display_data,
                        st.session_state.get('norm_date')
                    )

                    # Apply theme from settings
                    theme = SettingsManager.get_setting('theme')
                    fig = ChartManager.create_price_chart(data_normalized, log_scale, theme=theme)
                    DashboardLayout.render_main_area(fig)
                else:
                    st.info("Please select tickers to display")

            except Exception as e:
                st.error(f"Error processing data: {str(e)}")

        except Exception as e:
            if not isinstance(e, (tornado.websocket.WebSocketClosedError, tornado.iostream.StreamClosedError)):
                st.error(f"Application error: {str(e)}")
        finally:
            with handle_websocket_disconnect():
                StateManager.save_state()
                SettingsManager.save_settings()

if __name__ == "__main__":
    main()
