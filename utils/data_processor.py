from typing import Dict, Any
import pandas as pd
from datetime import datetime, date


def process_and_visualize_data(
        data_loaded: Dict[str, pd.DataFrame],
        user_inputs: Any,
        data_processor: 'DataProcessor'
) -> None:
    from dashboard.visualization import process_and_visualize_data
    process_and_visualize_data(data_loaded, user_inputs, data_processor)


class DataProcessor:
    @staticmethod
    def normalize_data(data_dict: Dict[str, pd.DataFrame], reference_date: datetime) -> Dict[str, pd.DataFrame]:
        normalized = {}
        for ticker, ticker_df in data_dict.items():
            if ticker_df.empty or reference_date not in ticker_df.index:
                normalized[ticker] = ticker_df
                continue
            # Normalize using vectorized operations
            ref_price = ticker_df.loc[reference_date]['close']
            norm_df = ticker_df.copy()
            norm_df['close'] = norm_df['close'] / ref_price
            normalized[ticker] = norm_df
        return normalized

    @staticmethod
    def adjust_range_and_interval(start_date: date, end_date: date, interval: str) -> str:
        date_diff = (end_date - start_date).days
        # Adjust interval based on date range
        if interval == "1d" and date_diff > 1825:
            interval = "1wk"
        elif interval == "1wk" and date_diff < 90:
            interval = "1d"
        return interval
