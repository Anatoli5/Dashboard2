from typing import Dict, List, Optional
import json
from pathlib import Path
import streamlit as st
from core.settings_manager import SettingsManager

class TickerLists:
    """Manages available tickers and user custom ticker lists"""
    
    # Default available tickers for each provider
    AVAILABLE_TICKERS = {
        'yahoo': {
            'crypto': [
                'BTC-USD', 'ETH-USD', 'ADA-USD', 'SOL-USD', 'XRP-USD',
                'DOGE-USD', 'DOT-USD', 'MATIC-USD', 'LINK-USD', 'UNI-USD'
            ],
            'stocks': [
                'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA',
                'JPM', 'V', 'WMT', 'JNJ', 'PG', 'XOM', 'BAC', 'MA'
            ],
            'indices': [
                '^GSPC', '^DJI', '^IXIC', '^RUT', '^VIX',
                '^FTSE', '^N225', '^GDAXI', '^FCHI'
            ]
        },
        'alphavantage': {
            'crypto': [
                'BTCUSD', 'ETHUSD', 'ADAUSD', 'SOLUSD', 'XRPUSD',
                'DOGEUSD', 'DOTUSD', 'MATICUSD', 'LINKUSD', 'UNIUSD'
            ],
            'stocks': [
                'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA',
                'JPM', 'V', 'WMT', 'JNJ', 'PG', 'XOM', 'BAC', 'MA'
            ],
            'indices': [
                'SPX', 'DJI', 'IXIC', 'RUT', 'VIX',
                'FTSE', 'N225', 'GDAXI', 'FCHI'
            ]
        }
    }

    # Provider-specific ticker mappings
    TICKER_MAPPINGS = {
        'yahoo_to_alphavantage': {
            'BTC-USD': 'BTCUSD',
            'ETH-USD': 'ETHUSD',
            'ADA-USD': 'ADAUSD',
            'SOL-USD': 'SOLUSD',
            'XRP-USD': 'XRPUSD',
            'DOGE-USD': 'DOGEUSD',
            'DOT-USD': 'DOTUSD',
            'MATIC-USD': 'MATICUSD',
            'LINK-USD': 'LINKUSD',
            'UNI-USD': 'UNIUSD',
            '^GSPC': 'SPX',
            '^DJI': 'DJI',
            '^IXIC': 'IXIC',
            '^RUT': 'RUT',
            '^VIX': 'VIX',
            '^FTSE': 'FTSE',
            '^N225': 'N225',
            '^GDAXI': 'GDAXI',
            '^FCHI': 'FCHI'
        }
    }

    # Add reverse mapping
    TICKER_MAPPINGS['alphavantage_to_yahoo'] = {
        v: k for k, v in TICKER_MAPPINGS['yahoo_to_alphavantage'].items()
    }

    LISTS_FILE = "ticker_lists.json"

    @staticmethod
    def initialize():
        """Initialize ticker lists state"""
        if 'ticker_lists' not in st.session_state:
            st.session_state.ticker_lists = TickerLists.load_lists()

    @staticmethod
    def load_lists() -> Dict:
        """Load saved ticker lists"""
        if Path(TickerLists.LISTS_FILE).exists():
            try:
                with open(TickerLists.LISTS_FILE, 'r') as f:
                    return json.load(f)
            except Exception as e:
                st.warning(f"Failed to load ticker lists: {str(e)}")
        
        # Return default structure if file doesn't exist or loading fails
        return {
            'lists': {
                'default': {
                    'name': 'Default List',
                    'description': 'Default ticker list',
                    'tickers': ['BTC-USD', 'ETH-USD'],
                    'provider': 'yahoo'
                }
            },
            'active_list': 'default'
        }

    @staticmethod
    def save_lists():
        """Save current ticker lists"""
        try:
            with open(TickerLists.LISTS_FILE, 'w') as f:
                json.dump(st.session_state.ticker_lists, f)
        except Exception as e:
            st.warning(f"Failed to save ticker lists: {str(e)}")

    @staticmethod
    def get_available_tickers(provider: Optional[str] = None, category: Optional[str] = None) -> List[str]:
        """Get available tickers for a provider and optional category"""
        if not provider:
            provider = SettingsManager.get_setting('data_provider')
        
        if category:
            return TickerLists.AVAILABLE_TICKERS.get(provider, {}).get(category, [])
        
        # Return all tickers if no category specified
        all_tickers = []
        for cat_tickers in TickerLists.AVAILABLE_TICKERS.get(provider, {}).values():
            all_tickers.extend(cat_tickers)
        return all_tickers

    @staticmethod
    def convert_ticker(ticker: str, from_provider: str, to_provider: str) -> str:
        """Convert ticker symbol between providers"""
        if from_provider == to_provider:
            return ticker
        
        mapping_key = f"{from_provider}_to_{to_provider}"
        if mapping_key in TickerLists.TICKER_MAPPINGS:
            return TickerLists.TICKER_MAPPINGS[mapping_key].get(ticker, ticker)
        
        # Try reverse mapping
        reverse_key = f"{to_provider}_to_{from_provider}"
        if reverse_key in TickerLists.TICKER_MAPPINGS:
            reverse_map = {v: k for k, v in TickerLists.TICKER_MAPPINGS[reverse_key].items()}
            return reverse_map.get(ticker, ticker)
        
        return ticker

    @staticmethod
    def create_list(name: str, description: str, tickers: List[str], provider: str) -> bool:
        """Create a new ticker list"""
        TickerLists.initialize()
        
        # Generate a unique key
        base_key = name.lower().replace(' ', '_')
        key = base_key
        counter = 1
        while key in st.session_state.ticker_lists['lists']:
            key = f"{base_key}_{counter}"
            counter += 1
        
        st.session_state.ticker_lists['lists'][key] = {
            'name': name,
            'description': description,
            'tickers': tickers,
            'provider': provider
        }
        
        TickerLists.save_lists()
        return True

    @staticmethod
    def update_list(list_key: str, tickers: List[str]) -> bool:
        """Update tickers in a list"""
        TickerLists.initialize()
        
        if list_key in st.session_state.ticker_lists['lists']:
            st.session_state.ticker_lists['lists'][list_key]['tickers'] = tickers
            TickerLists.save_lists()
            return True
        return False

    @staticmethod
    def delete_list(list_key: str) -> bool:
        """Delete a ticker list"""
        TickerLists.initialize()
        
        if list_key in st.session_state.ticker_lists['lists']:
            if list_key == 'default':
                st.error("Cannot delete the default list")
                return False
            
            del st.session_state.ticker_lists['lists'][list_key]
            
            # Switch to default list if active list was deleted
            if st.session_state.ticker_lists['active_list'] == list_key:
                st.session_state.ticker_lists['active_list'] = 'default'
            
            TickerLists.save_lists()
            return True
        return False

    @staticmethod
    def get_active_list() -> Dict:
        """Get currently active ticker list"""
        TickerLists.initialize()
        active_key = st.session_state.ticker_lists['active_list']
        return st.session_state.ticker_lists['lists'][active_key]

    @staticmethod
    def set_active_list(list_key: str) -> bool:
        """Set active ticker list"""
        TickerLists.initialize()
        
        if list_key in st.session_state.ticker_lists['lists']:
            st.session_state.ticker_lists['active_list'] = list_key
            TickerLists.save_lists()
            return True
        return False 