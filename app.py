# File: app.py

import streamlit as st
from datetime import datetime, timedelta
from core.data_manager import DatabaseManager
from core.utils import normalize_data, adjust_range_and_interval
from core.state_manager import StateManager
from ui.layout import DashboardLayout
from ui.sidebar import SidebarControls
from visualization.charts import ChartManager
from core.settings_manager import SettingsManager
from core.ticker_manager import TickerManager
import tornado.websocket
import contextlib
import atexit
import asyncio
import sys

def cleanup():
    """Cleanup function to be called on exit"""
    try:
        if not hasattr(st, 'session_state'):
            return
            
        # Save state
        if 'ticker_state' in st.session_state:
            try:
                state_data = {
                    'selected_tickers': st.session_state.ticker_state['selected_tickers']
                }
                StateManager.save_state(state_data)
            except Exception:
                pass
        
        # Save settings
        try:
            SettingsManager.save_settings()
        except Exception:
            pass
        
        # Close database connections
        if 'db_manager' in st.session_state:
            try:
                st.session_state.db_manager.engine.dispose()
            except Exception:
                pass
                
        # Clear session state
        try:
            st.session_state.clear()
        except Exception:
            pass
            
    except Exception:
        pass
    finally:
        # Ensure clean exit
        sys.exit(0)

@contextlib.contextmanager
def handle_websocket_disconnect():
    """Context manager to handle WebSocket disconnections gracefully"""
    try:
        yield
    except (tornado.websocket.WebSocketClosedError, 
            tornado.iostream.StreamClosedError,
            asyncio.CancelledError,
            RuntimeError,
            KeyboardInterrupt,
            SystemExit):
        cleanup()
    except Exception as e:
        cleanup()
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
            'log_scale': False,
            'theme': 'dark',
            'data_provider': 'yahoo'
        }

        for key, value in default_values.items():
            if key not in st.session_state:
                st.session_state[key] = value

def main():
    try:
        # Register cleanup on exit
        atexit.register(cleanup)
        
        with handle_websocket_disconnect():
            # Initialize settings and apply theme
            SettingsManager.initialize_settings()
            DashboardLayout.setup_page()
            
            # Initialize session state and ticker manager
            initialize_session_state()
            TickerManager.initialize()
            
            # Render sidebar controls and update session state
            SidebarControls.render_sidebar()
            
            # Initialize database manager with current settings
            current_provider = SettingsManager.get_setting('data_provider')
            if ('db_manager' not in st.session_state or 
                st.session_state.get('current_provider') != current_provider):
                try:
                    st.session_state.db_manager = DatabaseManager(
                        data_provider=current_provider,
                        api_key=SettingsManager.get_setting('alpha_vantage_key')
                    )
                    st.session_state.current_provider = current_provider
                except ValueError as e:
                    st.error(f"Error initializing data provider: {str(e)}")
                    return
            
            db_manager = st.session_state.db_manager
            
            # Get selected tickers
            selected_tickers = TickerManager.get_selected_tickers()
            
            # Adjust interval based on date range
            interval = adjust_range_and_interval(
                st.session_state['start_date'],
                st.session_state['end_date'],
                st.session_state['interval']
            )

            if selected_tickers:
                try:
                    # Get provider-specific tickers
                    provider_tickers = TickerManager.get_provider_tickers()
                    
                    # Update and load data
                    db_manager.update_ticker_data(provider_tickers, interval=interval)
                    data_loaded = db_manager.load_data_for_tickers(
                        provider_tickers,
                        st.session_state['start_date'],
                        st.session_state['end_date'],
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

                    # Normalize data if needed
                    data_normalized = normalize_data(
                        display_data,
                        st.session_state.get('norm_date')
                    )

                    # Create and render chart
                    theme = SettingsManager.get_setting('theme')
                    fig = ChartManager.create_price_chart(
                        data_normalized,
                        st.session_state['log_scale'],
                        theme=theme
                    )
                    DashboardLayout.render_main_area(fig)

                except Exception as e:
                    st.error(f"Error processing data: {str(e)}")
            else:
                st.info("Please select tickers to display")

    except Exception as e:
        if not isinstance(e, (tornado.websocket.WebSocketClosedError, 
                            tornado.iostream.StreamClosedError,
                            asyncio.CancelledError,
                            RuntimeError,
                            KeyboardInterrupt,
                            SystemExit)):
            st.error(f"Application error: {str(e)}")
    finally:
        # Ensure cleanup runs
        if 'db_manager' in st.session_state:
            st.session_state.db_manager.engine.dispose()

if __name__ == "__main__":
    main()
