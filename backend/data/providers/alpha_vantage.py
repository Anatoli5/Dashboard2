"""Alpha Vantage data provider implementation."""

import requests
import pandas as pd
from typing import Optional, Dict
from . import DataProvider


class AlphaVantageProvider(DataProvider):
    """Alpha Vantage data provider."""
    
    BASE_URL = "https://www.alphavantage.co/query"
    
    INTERVALS = {
        '1d': 'Daily',
        '1wk': 'Weekly',
        '1mo': 'Monthly'
    }
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Alpha Vantage provider."""
        self.api_key = api_key
        if not api_key:
            raise ValueError("API key is required for Alpha Vantage")
    
    def _make_request(self, params: Dict) -> Dict:
        """Make a request to Alpha Vantage API."""
        params['apikey'] = self.api_key
        response = requests.get(self.BASE_URL, params=params)
        response.raise_for_status()
        return response.json()
    
    def fetch_data(
        self,
        ticker: str,
        interval: str = '1d',
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """Fetch data from Alpha Vantage."""
        try:
            # Validate interval
            if interval not in self.INTERVALS:
                raise ValueError(f"Invalid interval: {interval}")
            
            # Prepare request parameters
            function = f"TIME_SERIES_{self.INTERVALS[interval]}"
            params = {
                'function': function,
                'symbol': ticker,
                'outputsize': 'full'
            }
            
            # Make request
            data = self._make_request(params)
            
            # Parse response
            time_series_key = [k for k in data.keys() if 'Time Series' in k][0]
            df = pd.DataFrame.from_dict(data[time_series_key], orient='index')
            
            # Clean column names
            df.columns = [col.split('. ')[1].lower() for col in df.columns]
            df.index = pd.to_datetime(df.index)
            df.index.name = 'date'
            
            # Convert values to float
            for col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Filter by date if provided
            if start_date:
                df = df[df.index >= pd.to_datetime(start_date)]
            if end_date:
                df = df[df.index <= pd.to_datetime(end_date)]
            
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
        """Validate if a ticker exists on Alpha Vantage."""
        try:
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': ticker
            }
            data = self._make_request(params)
            return 'Global Quote' in data and data['Global Quote']
        except:
            return False 