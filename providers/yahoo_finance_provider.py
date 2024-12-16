import pandas as pd
import yfinance as yf
from datetime import date
from typing import Optional
from providers.base_provider import BaseProvider


class YahooFinanceProvider(BaseProvider):
    """
    Data provider for Yahoo Finance.
    """

    def fetch_data(
            self,
            ticker: str,
            start_date: Optional[date] = None,
            interval: str = "1d"
    ) -> pd.DataFrame:
        """
        Fetches data from Yahoo Finance.

        Args:
            ticker (str): The ticker symbol.
            start_date (Optional[date]): The starting date for data retrieval.
            interval (str): Data interval.

        Returns:
            pd.DataFrame: DataFrame containing the fetched data.
        """
        fetched_df = yf.download(
            ticker,
            start=start_date,
            interval=interval,
            auto_adjust=True,
            progress=False
        )
        return fetched_df
