from typing import Dict, List, Optional
import pandas as pd
import streamlit as st
from core.settings_manager import SettingsManager
from core.state_manager import StateManager

class TickerManager:
    """Manages ticker lists and mappings for different data providers"""
    
    # Provider-specific ticker mappings
    PROVIDER_MAPPINGS = {
        'yahoo': {
            'BTC-USD': 'BTC-USD',
            'ETH-USD': 'ETH-USD',
            'ADA-USD': 'ADA-USD',
            'SOL-USD': 'SOL-USD',
            'XRP-USD': 'XRP-USD',
            'DOGE-USD': 'DOGE-USD',
            'DOT-USD': 'DOT-USD',
            'MATIC-USD': 'MATIC-USD',
            'LINK-USD': 'LINK-USD',
            'UNI-USD': 'UNI-USD'
        },
        'alpha_vantage': {
            'BTC-USD': 'BTCUSD',
            'ETH-USD': 'ETHUSD',
            'ADA-USD': 'ADAUSD',
            'SOL-USD': 'SOLUSD',
            'XRP-USD': 'XRPUSD',
            'DOGE-USD': 'DOGEUSD',
            'DOT-USD': 'DOTUSD',
            'MATIC-USD': 'MATICUSD',
            'LINK-USD': 'LINKUSD',
            'UNI-USD': 'UNIUSD'
        }
    }

    @staticmethod
    def initialize():
        """Initialize ticker state"""
        if 'ticker_state' not in st.session_state:
            # Try to load from saved state first
            saved_tickers = []
            try:
                saved_state = StateManager.load_state()
                if isinstance(saved_state, dict) and 'selected_tickers' in saved_state:
                    saved_tickers = saved_state['selected_tickers']
            except Exception:
                pass

            st.session_state.ticker_state = {
                'selected_tickers': saved_tickers,
                'provider_tickers': {},
                'last_provider': None
            }

    @staticmethod
    def save_state():
        """Save ticker state"""
        if 'ticker_state' in st.session_state:
            try:
                state_data = {
                    'selected_tickers': st.session_state.ticker_state['selected_tickers']
                }
                StateManager.save_state(state_data)
            except Exception as e:
                st.warning(f"Failed to save ticker state: {str(e)}")

    @staticmethod
    def get_available_tickers(provider: Optional[str] = None) -> List[str]:
        """Get available tickers for the current or specified provider"""
        if not provider:
            provider = SettingsManager.get_setting('data_provider')
        return list(TickerManager.PROVIDER_MAPPINGS.get(provider, {}).keys())

    @staticmethod
    def get_provider_ticker(ticker: str, provider: Optional[str] = None) -> str:
        """Convert display ticker to provider-specific ticker"""
        if not provider:
            provider = SettingsManager.get_setting('data_provider')
        mapping = TickerManager.PROVIDER_MAPPINGS.get(provider, {})
        return mapping.get(ticker, ticker)

    @staticmethod
    def get_display_ticker(provider_ticker: str, provider: Optional[str] = None) -> Optional[str]:
        """Convert provider-specific ticker to display ticker"""
        if not provider:
            provider = SettingsManager.get_setting('data_provider')
        mapping = TickerManager.PROVIDER_MAPPINGS.get(provider, {})
        # Reverse lookup in the mapping
        for display_ticker, prov_ticker in mapping.items():
            if prov_ticker == provider_ticker:
                return display_ticker
        return None

    @staticmethod
    def get_selected_tickers() -> List[str]:
        """Get currently selected tickers"""
        TickerManager.initialize()
        return st.session_state.ticker_state.get('selected_tickers', [])

    @staticmethod
    def set_selected_tickers(tickers: List[str]):
        """Set selected tickers and save state"""
        TickerManager.initialize()
        st.session_state.ticker_state['selected_tickers'] = tickers
        TickerManager.save_state()

    @staticmethod
    def get_provider_tickers(provider: Optional[str] = None) -> List[str]:
        """Get provider-specific tickers for selected tickers"""
        if not provider:
            provider = SettingsManager.get_setting('data_provider')
        
        selected_tickers = TickerManager.get_selected_tickers()
        return [TickerManager.get_provider_ticker(ticker, provider) for ticker in selected_tickers]

    @staticmethod
    def add_ticker(provider_ticker: str, provider: Optional[str] = None) -> bool:
        """Add a provider-specific ticker to the selection"""
        if not provider:
            provider = SettingsManager.get_setting('data_provider')
        
        # Convert provider ticker to display ticker
        display_ticker = TickerManager.get_display_ticker(provider_ticker, provider)
        if not display_ticker:
            # If no mapping exists, use the provider ticker as display ticker
            display_ticker = provider_ticker
        
        current_tickers = TickerManager.get_selected_tickers()
        if display_ticker not in current_tickers:
            TickerManager.set_selected_tickers(current_tickers + [display_ticker])
            return True
        return False

    @staticmethod
    def render_ticker_selection() -> List[str]:
        """Render ticker selection UI"""
        TickerManager.initialize()
        available_tickers = TickerManager.get_available_tickers()
        current_provider = SettingsManager.get_setting('data_provider')
        
        # Check if provider has changed
        last_provider = st.session_state.ticker_state.get('last_provider')
        if last_provider != current_provider:
            st.session_state.ticker_state['last_provider'] = current_provider
            # Keep existing selections if they're valid in the new provider
            valid_tickers = [t for t in TickerManager.get_selected_tickers() if t in available_tickers]
            if not valid_tickers:
                valid_tickers = ["BTC-USD", "ETH-USD"] if all(t in available_tickers for t in ["BTC-USD", "ETH-USD"]) else available_tickers[:2]
            TickerManager.set_selected_tickers(valid_tickers)
        
        # Initialize with default tickers if empty
        if not TickerManager.get_selected_tickers():
            default_tickers = ["BTC-USD", "ETH-USD"] if all(t in available_tickers for t in ["BTC-USD", "ETH-USD"]) else available_tickers[:2]
            TickerManager.set_selected_tickers(default_tickers)

        st.sidebar.subheader("Select Tickers")
        selected = st.sidebar.multiselect(
            f"Available Tickers ({current_provider})",
            available_tickers,
            default=TickerManager.get_selected_tickers(),
            key=f"ticker_select_{current_provider}"  # Unique key for each provider
        )
        
        if selected != TickerManager.get_selected_tickers():
            TickerManager.set_selected_tickers(selected)

        return selected