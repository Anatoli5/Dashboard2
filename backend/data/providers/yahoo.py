"""Yahoo Finance data provider implementation."""

import yfinance as yf
import pandas as pd
from typing import Optional
from . import DataProvider


class YahooProvider(DataProvider):
    """Yahoo Finance data provider."""
    
    INTERVALS = {
        '1d': '1d',
        '1wk': '1wk',
        '1mo': '1mo'
    }
    
    def __init__(self):
        """Initialize the Yahoo Finance provider."""
        self.session = None
        
    def _get_session(self):
        """Get or create a yfinance session."""
        if self.session is None:
            self.session = yf.Ticker('')  # Create a dummy ticker to get session
        return self.session
    
    def fetch_data(
        self,
        ticker: str,
        interval: str = '1d',
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """Fetch data from Yahoo Finance."""
        try:
            # Validate interval
            if interval not in self.INTERVALS:
                raise ValueError(f"Invalid interval: {interval}")
            
            # Create ticker object
            yf_ticker = yf.Ticker(ticker)
            
            # Fetch data
            df = yf_ticker.history(
                interval=self.INTERVALS[interval],
                start=start_date,
                end=end_date
            )
            
            # Standardize column names
            df.index.name = 'date'
            df.columns = df.columns.str.lower()
            
            # Ensure all required columns exist
            required_columns = ['open', 'high', 'low', 'close', 'volume']
            for col in required_columns:
                if col not in df.columns:
                    df[col] = 0
            
            return df[required_columns]
            
        except Exception as e:
            print(f"Error fetching data for {ticker}: {str(e)}")
            return pd.DataFrame()
    
    def validate_ticker(self, ticker: str) -> bool:
        """Validate if a ticker exists on Yahoo Finance."""
        try:
            yf_ticker = yf.Ticker(ticker)
            info = yf_ticker.info
            return 'regularMarketPrice' in info
        except:
            return False 