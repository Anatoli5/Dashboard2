import streamlit as st
from datetime import datetime, timedelta
from core.settings_manager import SettingsManager
from core.ticker_manager import TickerManager
from core.symbol_search import SymbolSearch


class SidebarControls:
    @staticmethod
    def render_sidebar() -> None:
        """Render the sidebar controls"""
        st.sidebar.title("Dashboard Controls")
        
        # Settings section
        with st.sidebar.expander("⚙️ Settings", expanded=False):
            # Theme selector
            current_theme = SettingsManager.get_setting('theme', 'dark')
            new_theme = st.selectbox(
                "Theme",
                options=['dark', 'light'],
                index=0 if current_theme == 'dark' else 1,
                key='theme_selector'
            )
            if new_theme != current_theme:
                SettingsManager.set_setting('theme', new_theme)
                st.rerun()
            
            # Data provider selector
            current_provider = SettingsManager.get_setting('data_provider', 'yahoo')
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
                st.rerun()

        st.sidebar.markdown("---")

        # Ticker selection
        st.sidebar.subheader("Ticker Selection")
        
        # Symbol search for Alpha Vantage
        if SettingsManager.get_setting('data_provider') == 'alphavantage':
            search_query = st.sidebar.text_input(
                "Search Symbols",
                key="symbol_search",
                help="Enter keywords to search for symbols"
            )
            
            if search_query:
                results = SymbolSearch.search_symbols(search_query)
                if results:
                    selected_symbol = st.sidebar.selectbox(
                        "Found Symbols",
                        options=[f"{r['symbol']} - {r['name']}" for r in results],
                        format_func=lambda x: x.split(' - ')[0]
                    )
                    if st.sidebar.button("Add Symbol"):
                        symbol = selected_symbol.split(' - ')[0]
                        TickerManager.add_ticker(symbol)
                        st.rerun()
                else:
                    st.sidebar.info("No symbols found")
        
        # Display selected tickers
        selected_tickers = TickerManager.get_selected_tickers()
        if selected_tickers:
            st.sidebar.write("Selected Tickers:")
            cols = st.sidebar.columns([3, 1])
            for ticker in selected_tickers:
                cols[0].write(f"• {ticker}")
                if cols[1].button("❌", key=f"remove_{ticker}"):
                    TickerManager.remove_ticker(ticker)
                    st.rerun()
        
        st.sidebar.markdown("---")

        # Date range selection
        st.sidebar.subheader("Date Range")
        end_date = st.sidebar.date_input(
            "End Date",
            value=st.session_state.get('end_date', datetime.now().date()),
            max_value=datetime.now().date(),
            key="end_date"
        )
        start_date = st.sidebar.date_input(
            "Start Date",
            value=st.session_state.get('start_date', (datetime.now() - timedelta(days=365)).date()),
            max_value=end_date,
            key="start_date"
        )
        
        # Interval selection
        st.sidebar.subheader("Interval")
        interval = st.sidebar.selectbox(
            "Select Interval",
            options=['1d', '1wk', '1mo'],
            index=['1d', '1wk', '1mo'].index(st.session_state.get('interval', '1d')),
            key="interval"
        )
        
        # Chart options
        st.sidebar.subheader("Chart Options")
        log_scale = st.sidebar.checkbox(
            "Logarithmic Scale",
            value=st.session_state.get('log_scale', False),
            key="log_scale"
        )
        
        # Clear normalization
        if st.session_state.get('norm_date'):
            if st.sidebar.button("Clear Normalization"):
                st.session_state['norm_date'] = None
                st.rerun()
            st.sidebar.info(
                "📌 Normalized to: " + 
                st.session_state['norm_date'].strftime('%Y-%m-%d')
            )
