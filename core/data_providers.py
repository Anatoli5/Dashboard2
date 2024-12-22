from abc import ABC, abstractmethod
import pandas as pd
from datetime import datetime
import yfinance as yf
import requests
import time
from typing import Optional
import streamlit as st
from core.request_manager import RequestManager
from core.settings_manager import SettingsManager

class DataProvider(ABC):
    """Abstract base class for data providers"""
    
    @abstractmethod
    def fetch_data(self, ticker: str, interval: str = "1d", period: str = "max") -> pd.DataFrame:
        """Fetch data for a given ticker"""
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Get the name of the data provider"""
        pass

class YahooFinanceProvider(DataProvider):
    """Yahoo Finance data provider implementation"""
    
    def get_provider_name(self) -> str:
        return "Yahoo Finance"

    def fetch_data(self, ticker: str, interval: str = "1d", period: str = "max") -> pd.DataFrame:
        """Fetch data from Yahoo Finance with improved retry mechanism"""
        max_retries = 3
        base_delay = 2
        
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    delay = base_delay * (2 ** (attempt - 1))
                    time.sleep(delay)
                    st.info(f"Retrying {ticker} (attempt {attempt + 1}/{max_retries})...")
                
                df = yf.download(
                    ticker,
                    period=period,
                    interval=interval,
                    auto_adjust=True,
                    progress=False,
                    timeout=10
                )
                
                if not df.empty:
                    return df
                else:
                    st.warning(f"No data received for {ticker}, attempt {attempt + 1}/{max_retries}")
                    
            except Exception as e:
                if attempt == max_retries - 1:
                    st.error(f"Failed to fetch {ticker} after {max_retries} attempts: {str(e)}")
                continue
        return pd.DataFrame()

class AlphaVantageProvider(DataProvider):
    """Alpha Vantage data provider implementation"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or st.secrets.get("ALPHA_VANTAGE_API_KEY")
        if not self.api_key:
            raise ValueError("Alpha Vantage API key is required")
        self.base_url = "https://www.alphavantage.co/query"

    def get_provider_name(self) -> str:
        return "Alpha Vantage"

    def _interval_to_function(self, interval: str) -> tuple:
        """Convert generic interval to Alpha Vantage specific function and interval"""
        interval_mapping = {
            "1d": ("TIME_SERIES_DAILY_ADJUSTED", "Daily"),
            "1wk": ("TIME_SERIES_WEEKLY_ADJUSTED", "Weekly"),
            "1mo": ("TIME_SERIES_MONTHLY_ADJUSTED", "Monthly")
        }
        return interval_mapping.get(interval, ("TIME_SERIES_DAILY_ADJUSTED", "Daily"))

    def fetch_data(self, ticker: str, interval: str = "1d", period: str = "max") -> pd.DataFrame:
        """Fetch data from Alpha Vantage"""
        request_manager = RequestManager.get_instance()
        request_manager.set_cache_timeout(
            SettingsManager.get_setting('cache_timeout', 3600)
        )
        
        # Check if it's a crypto ticker
        is_crypto = ticker.endswith('USD') and any(c in ticker for c in ['BTC', 'ETH', 'ADA', 'SOL', 'XRP', 'DOGE', 'DOT', 'MATIC', 'LINK', 'UNI'])
        
        if is_crypto:
            params = {
                'function': 'DIGITAL_CURRENCY_DAILY',
                'symbol': ticker[:-3],  # Remove USD suffix
                'market': 'USD',
                'apikey': self.api_key
            }
        else:
            function, output_size = self._interval_to_function(interval)
            params = {
                'function': function,
                'symbol': ticker,
                'apikey': self.api_key,
                'outputsize': 'full'
            }
        
        try:
            # Use asyncio to run the async request
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            data = loop.run_until_complete(
                request_manager.request('alpha_vantage', self.base_url, params)
            )
            loop.close()
            
            # Debug: Print response structure
            if 'Error Message' in data:
                st.error(f"API Error for {ticker}: {data['Error Message']}")
                return pd.DataFrame()
            
            # Handle different response formats for crypto vs stocks
            if is_crypto:
                time_series_key = 'Time Series (Digital Currency Daily)'
                if time_series_key not in data:
                    st.warning(f"No data received for {ticker}")
                    if 'Note' in data:
                        st.warning(f"API Note: {data['Note']}")
                    return pd.DataFrame()
                
                # Convert crypto data format
                raw_data = data[time_series_key]
                df = pd.DataFrame.from_dict(raw_data, orient='index')
                df.index.name = 'Date'
                
                # Debug: Print available columns
                st.write(f"Available columns for {ticker}: {df.columns.tolist()}")
                
                # For crypto, we need to use the regular column names
                column_mapping = {
                    '1. open': 'Open',
                    '2. high': 'High',
                    '3. low': 'Low',
                    '4. close': 'Close',
                    '5. volume': 'Volume'
                }
                
                # Rename columns first
                df = df.rename(columns=column_mapping)
                
            else:
                time_series_key = f"Time Series ({output_size})"
                if time_series_key not in data:
                    st.warning(f"No data received for {ticker}")
                    if 'Note' in data:
                        st.warning(f"API Note: {data['Note']}")
                    return pd.DataFrame()
                
                # Convert stock data format
                df = pd.DataFrame.from_dict(data[time_series_key], orient='index')
                df.index.name = 'Date'
                
                # Rename stock columns
                column_mapping = {
                    '1. open': 'Open',
                    '2. high': 'High',
                    '3. low': 'Low',
                    '4. close': 'Close',
                    '5. volume': 'Volume'
                }
                df = df.rename(columns=column_mapping)
            
            # Reset index to get Date as a column, then set it back as index
            df = df.reset_index()
            df['Date'] = pd.to_datetime(df['Date'])
            df = df.set_index('Date')
            
            # Convert numeric columns
            for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Sort index in ascending order
            df = df.sort_index()
            
            # Verify we have the required columns
            required_columns = {'Open', 'High', 'Low', 'Close', 'Volume'}
            missing_columns = required_columns - set(df.columns)
            if missing_columns:
                st.warning(f"Missing columns for {ticker}: {missing_columns}")
                st.write(f"Available columns: {df.columns.tolist()}")
                return pd.DataFrame()
            
            return df
            
        except Exception as e:
            st.error(f"Error fetching data for {ticker}: {str(e)}")
            return pd.DataFrame()

def get_data_provider(provider_name: str = "yahoo", api_key: Optional[str] = None) -> DataProvider:
    """Factory function to get the appropriate data provider"""
    providers = {
        "yahoo": YahooFinanceProvider,
        "alpha_vantage": lambda: AlphaVantageProvider(api_key)
    }
    
    provider_func = providers.get(provider_name.lower())
    if not provider_func:
        raise ValueError(f"Unknown provider: {provider_name}")
    
    return provider_func() 