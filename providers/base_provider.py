from abc import ABC, abstractmethod
import pandas as pd
from typing import Optional
from datetime import date


class BaseProvider(ABC):
    """
    Abstract base class for data providers.
    """

    @abstractmethod
    def fetch_data(
            self,
            ticker: str,
            start_date: Optional[date] = None,
            interval: str = "1d"
    ) -> pd.DataFrame:
        """
        Fetches data for the specified ticker.

        Args:
            ticker (str): The ticker symbol.
            start_date (Optional[date]): The starting date for data retrieval.
            interval (str): Data interval (e.g., '1d', '1wk', '1mo').

        Returns:
            pd.DataFrame: DataFrame containing the fetched data.
        """
        pass
