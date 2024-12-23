"""Data provider interfaces and factory."""

from abc import ABC, abstractmethod
from typing import Dict, Optional
import pandas as pd


class DataProvider(ABC):
    """Abstract base class for data providers."""
    
    @abstractmethod
    def fetch_data(
        self,
        ticker: str,
        interval: str = '1d',
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """Fetch data for a given ticker.
        
        Args:
            ticker: The ticker symbol
            interval: Data interval ('1d', '1wk', '1mo')
            start_date: Start date for data fetch
            end_date: End date for data fetch
            
        Returns:
            DataFrame with columns: [date, open, high, low, close, volume]
        """
        pass
    
    @abstractmethod
    def validate_ticker(self, ticker: str) -> bool:
        """Validate if a ticker is available in this provider."""
        pass


def get_provider(name: str, api_key: Optional[str] = None) -> DataProvider:
    """Get a data provider instance by name."""
    from .yahoo import YahooProvider
    from .alpha_vantage import AlphaVantageProvider
    
    providers: Dict[str, type] = {
        'yahoo': YahooProvider,
        'alphavantage': AlphaVantageProvider
    }
    
    if name not in providers:
        raise ValueError(f"Unknown provider: {name}")
    
    provider_class = providers[name]
    return provider_class(api_key) if api_key else provider_class() 