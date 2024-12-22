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
from ui.ticker_lists import TickerListsUI
import tornado.websocket
import contextlib
import atexit
import asyncio
import sys
import pandas as pd
from streamlit_plotly_events import plotly_events

# Global flags
_cleanup_done = False

def initialize_session_state():
    """Initialize all session state variables"""
    if 'initialized' not in st.session_state:
        defaults = {
            'initialized': True,
            'norm_date': None,
            'start_date': (datetime.now() - timedelta(days=365)).date(),
            'end_date': datetime.now().date(),
            'interval': '1d',
            'log_scale': False,
            'theme': SettingsManager.get_setting('theme', 'dark'),
            'data_provider': SettingsManager.get_setting('data_provider', 'yahoo'),
            'db_manager': None,
            'current_provider': None,
            'data_cache': {},
            'cached_interval': None,
            'needs_rerun': False,
            'is_normalizing': False
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value

def sync_settings():
    """Synchronize settings with session state"""
    if not hasattr(st, 'session_state'):
        return
        
    theme = SettingsManager.get_setting('theme', 'dark')
    provider = SettingsManager.get_setting('data_provider', 'yahoo')
    
    if theme != st.session_state.theme:
        st.session_state.theme = theme
        st.session_state.needs_rerun = True
        
    if provider != st.session_state.data_provider:
        st.session_state.data_provider = provider
        st.session_state.needs_rerun = True
        st.session_state.data_cache = {}
        st.session_state.cached_interval = None

def cleanup():
    """Cleanup function to be called on exit"""
    global _cleanup_done
    if _cleanup_done:
        return
        
    try:
        # Save settings first
        SettingsManager.save_settings()
        
        if hasattr(st, 'session_state'):
            # Save state
            if 'ticker_state' in st.session_state:
                state_data = {
                    'selected_tickers': st.session_state.ticker_state['selected_tickers']
                }
                StateManager.save_state(state_data)
            
            # Close database connections
            if 'db_manager' in st.session_state and st.session_state.db_manager:
                st.session_state.db_manager.engine.dispose()
                
            # Clear cache
            if 'data_cache' in st.session_state:
                st.session_state.data_cache = {}
            if 'cached_interval' in st.session_state:
                st.session_state.cached_interval = None
                
    except Exception:
        pass
        
    _cleanup_done = True

def get_or_create_db_manager():
    """Get existing or create new database manager"""
    if not hasattr(st, 'session_state'):
        return None
        
    current_provider = st.session_state.data_provider
    
    if (st.session_state.db_manager is None or 
        st.session_state.current_provider != current_provider):
        try:
            if st.session_state.db_manager is not None:
                st.session_state.db_manager.engine.dispose()
                
            st.session_state.db_manager = DatabaseManager(
                data_provider=current_provider,
                api_key=SettingsManager.get_setting('alpha_vantage_key')
            )
            st.session_state.current_provider = current_provider
            st.session_state.data_cache = {}
            st.session_state.cached_interval = None
        except ValueError as e:
            st.error(f"Error initializing data provider: {str(e)}")
            return None
            
    return st.session_state.db_manager

@contextlib.contextmanager
def handle_cleanup():
    """Context manager to handle cleanup"""
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

def main():
    """Main application function"""
    try:
        # Register cleanup
        atexit.register(cleanup)
        
        with handle_cleanup():
            # Initialize settings and state
            SettingsManager.initialize_settings()
            initialize_session_state()
            sync_settings()
            
            # Setup page and apply theme
            DashboardLayout.setup_page()
            
            # Render sidebar controls
            SidebarControls.render_sidebar()
            
            # Get or create database manager
            db_manager = get_or_create_db_manager()
            if not db_manager:
                return
            
            # Get selected tickers from active list
            selected_tickers = TickerListsUI.get_selected_tickers()
            
            # Cache interval calculation
            interval = st.session_state.cached_interval
            if not interval:
                interval = adjust_range_and_interval(
                    st.session_state.start_date,
                    st.session_state.end_date,
                    st.session_state.interval
                )
                st.session_state.cached_interval = interval

            if selected_tickers:
                try:
                    # Cache provider tickers mapping
                    current_provider = st.session_state.current_provider
                    provider_tickers = [
                        TickerManager.get_provider_ticker(ticker, current_provider)
                        for ticker in selected_tickers
                    ]
                    
                    # Update and load data with caching
                    cache_key = f"{','.join(provider_tickers)}_{interval}"
                    
                    if cache_key not in st.session_state.data_cache:
                        db_manager.update_ticker_data(provider_tickers, interval=interval)
                        data_loaded = db_manager.load_data_for_tickers(
                            provider_tickers,
                            st.session_state.start_date,
                            st.session_state.end_date,
                            interval=interval
                        )
                        st.session_state.data_cache[cache_key] = data_loaded
                    else:
                        data_loaded = st.session_state.data_cache[cache_key]

                    if not any(not df.empty for df in data_loaded.values()):
                        st.warning("No data available for the selected tickers and time range.")
                        return

                    # Map the data back to display tickers
                    display_data = {
                        ticker: data_loaded[TickerManager.get_provider_ticker(ticker, current_provider)]
                        for ticker in selected_tickers
                        if TickerManager.get_provider_ticker(ticker, current_provider) in data_loaded
                    }

                    # Handle normalization with state management
                    norm_date = st.session_state.get('norm_date')
                    if norm_date and not st.session_state.get('is_normalizing'):
                        st.session_state.is_normalizing = True
                        display_data = normalize_data(display_data, norm_date)
                        st.session_state.is_normalizing = False

                    # Create and render chart
                    fig = ChartManager.create_price_chart(
                        display_data,
                        st.session_state.log_scale,
                        theme=st.session_state.theme
                    )
                    DashboardLayout.render_main_area(fig)

                    # Handle click events for normalization
                    clicked_points = plotly_events(
                        fig,
                        click_event=True,
                        hover_event=False,
                        select_event=False,
                        key="plot"
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
                    if st.session_state.get('norm_date'):
                        st.write("**Normalization Reference Date:**", st.session_state.norm_date.strftime('%Y-%m-%d'))

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
        if not _cleanup_done:
            cleanup()

if __name__ == "__main__":
    main()
