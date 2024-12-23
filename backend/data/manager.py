"""Data manager for coordinating data providers and database operations."""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd

from .providers import get_provider, DataProvider
from .database.operations import DatabaseOperations
from config.settings import DATA_SETTINGS


class DataManager:
    """Manages data operations between providers and database."""
    
    def __init__(self, provider_name: str = None, api_key: Optional[str] = None):
        """Initialize the data manager.
        
        Args:
            provider_name: Name of the data provider to use
            api_key: API key for the provider if required
        """
        self.provider_name = provider_name or DATA_SETTINGS['default_provider']
        self.provider = get_provider(self.provider_name, api_key)
        self.db = DatabaseOperations()
        
    def update_ticker_data(
        self,
        tickers: List[str],
        interval: str = None,
        force: bool = False
    ) -> None:
        """Update data for given tickers.
        
        Args:
            tickers: List of ticker symbols to update
            interval: Data interval ('1d', '1wk', '1mo')
            force: Whether to force update regardless of last update time
        """
        interval = interval or DATA_SETTINGS['default_interval']
        
        for ticker in tickers:
            try:
                # Check if update is needed
                if not force:
                    last_update = self.db.get_last_update(
                        ticker,
                        self.provider_name,
                        interval
                    )
                    if last_update and datetime.now() - last_update < timedelta(minutes=DATA_SETTINGS['cache_timeout']):
                        continue
                
                # Fetch new data
                df = self.provider.fetch_data(ticker, interval=interval)
                if not df.empty:
                    self.db.save_ticker_data(
                        ticker,
                        df,
                        interval,
                        self.provider_name
                    )
                    
            except Exception as e:
                print(f"Error updating {ticker}: {str(e)}")
    
    def load_data_for_tickers(
        self,
        tickers: List[str],
        start_date: datetime,
        end_date: datetime,
        interval: str = None
    ) -> Dict[str, pd.DataFrame]:
        """Load data for multiple tickers.
        
        Args:
            tickers: List of ticker symbols to load
            start_date: Start date for data
            end_date: End date for data
            interval: Data interval ('1d', '1wk', '1mo')
            
        Returns:
            Dictionary mapping tickers to their data DataFrames
        """
        interval = interval or DATA_SETTINGS['default_interval']
        result = {}
        
        for ticker in tickers:
            try:
                df = self.db.load_ticker_data(
                    ticker,
                    interval,
                    start_date,
                    end_date
                )
                result[ticker] = df
            except Exception as e:
                print(f"Error loading {ticker}: {str(e)}")
                result[ticker] = pd.DataFrame()
        
        return result
    
    def validate_tickers(self, tickers: List[str]) -> Dict[str, bool]:
        """Validate multiple tickers.
        
        Args:
            tickers: List of ticker symbols to validate
            
        Returns:
            Dictionary mapping tickers to their validity
        """
        return {
            ticker: self.provider.validate_ticker(ticker)
            for ticker in tickers
        }
    
    def cleanup(self, days: int = 30) -> None:
        """Clean up old data.
        
        Args:
            days: Number of days of data to keep
        """
        try:
            self.db.cleanup_old_data(days)
        except Exception as e:
            print(f"Error during cleanup: {str(e)}") 