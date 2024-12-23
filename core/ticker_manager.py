from typing import Dict, List, Optional
import pandas as pd
from core.state_manager import StateManager
from config.settings import TICKER_LISTS

class TickerManager:
    """Manages ticker lists and provider mappings."""
    
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
    
    @classmethod
    def initialize(cls) -> None:
        """Initialize ticker state."""
        state = StateManager.load_state()
        if 'selected_tickers' not in state:
            # Set default tickers
            default_tickers = ["BTC-USD", "ETH-USD"]
            StateManager.set_state('selected_tickers', default_tickers)
    
    @classmethod
    def get_provider_ticker(cls, ticker: str, provider: str = 'yahoo') -> str:
        """Convert display ticker to provider-specific ticker."""
        mapping = cls.PROVIDER_MAPPINGS.get(provider, {})
        return mapping.get(ticker, ticker)
    
    @classmethod
    def get_display_ticker(cls, provider_ticker: str, provider: str = 'yahoo') -> Optional[str]:
        """Convert provider-specific ticker to display ticker."""
        mapping = cls.PROVIDER_MAPPINGS.get(provider, {})
        for display_ticker, prov_ticker in mapping.items():
            if prov_ticker == provider_ticker:
                return display_ticker
        return provider_ticker
    
    @classmethod
    def get_selected_tickers(cls) -> List[str]:
        """Get currently selected tickers."""
        cls.initialize()
        return StateManager.get_state('selected_tickers', [])
    
    @classmethod
    def set_selected_tickers(cls, tickers: List[str]) -> None:
        """Set selected tickers."""
        StateManager.set_state('selected_tickers', tickers)
    
    @classmethod
    def add_ticker(cls, ticker: str) -> bool:
        """Add a ticker to selection."""
        current_tickers = cls.get_selected_tickers()
        if ticker not in current_tickers:
            current_tickers.append(ticker)
            cls.set_selected_tickers(current_tickers)
            return True
        return False
    
    @classmethod
    def remove_ticker(cls, ticker: str) -> bool:
        """Remove a ticker from selection."""
        current_tickers = cls.get_selected_tickers()
        if ticker in current_tickers:
            current_tickers.remove(ticker)
            cls.set_selected_tickers(current_tickers)
            return True
        return False
    
    @classmethod
    def get_available_tickers(cls) -> List[Dict]:
        """Get all available tickers with categories."""
        available_tickers = []
        for category, tickers in TICKER_LISTS.items():
            for ticker in tickers:
                available_tickers.append({
                    'label': f"{ticker} ({category})",
                    'value': ticker
                })
        return available_tickers
    
    @classmethod
    def get_tickers_by_category(cls, category: str) -> List[str]:
        """Get tickers for a specific category."""
        return TICKER_LISTS.get(category, [])