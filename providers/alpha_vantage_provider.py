import pandas as pd
import requests
from datetime import date
from typing import Optional
from providers.base_provider import BaseProvider
from config.settings import ALPHA_VANTAGE_API_KEY


class AlphaVantageProvider(BaseProvider):
    """
    Data provider for Alpha Vantage.
    """

    def fetch_data(
            self,
            ticker: str,
            start_date: Optional[date] = None,
            interval: str = "1d"
    ) -> pd.DataFrame:
        """
        Fetches data from Alpha Vantage.

        Args:
            ticker (str): The ticker symbol.
            start_date (Optional[date]): The starting date for data retrieval.
            interval (str): Data interval.

        Returns:
            pd.DataFrame: DataFrame containing the fetched data.
        """
        # Placeholder implementation; replace with actual Alpha Vantage API calls
        params = {
            'function': 'TIME_SERIES_DAILY_ADJUSTED',
            'symbol': ticker,
            'apikey': ALPHA_VANTAGE_API_KEY,
            'outputsize': 'full'
        }
        url = 'https://www.alphavantage.co/query'
        response = requests.get(url, params=params)
        data = response.json()

        # Convert JSON data to DataFrame
        time_series = data.get('Time Series (Daily)', {})
        df = pd.DataFrame.from_dict(time_series, orient='index')
        df.index = pd.to_datetime(df.index)
        df = df.rename(columns={
            '1. open': 'Open',
            '2. high': 'High',
            '3. low': 'Low',
            '4. close': 'Close',
            '5. adjusted close': 'Adj Close',
            '6. volume': 'Volume'
        })
        df = df.sort_index()
        # Filter by start_date if provided
        if start_date:
            df = df[df.index >= pd.to_datetime(start_date)]
        return df
