# File: core/utils.py

import pandas as pd
from datetime import datetime
import streamlit as st
from typing import Dict


def normalize_data(data_dict: Dict[str, pd.DataFrame], reference_date) -> Dict[str, pd.DataFrame]:
    """Normalize price data relative to a reference date"""
    if reference_date is None:
        return data_dict

    normalized = {}
    try:
        # Ensure reference_date is pandas Timestamp
        if not isinstance(reference_date, pd.Timestamp):
            reference_date = pd.to_datetime(reference_date)

        for ticker, ticker_df in data_dict.items():
            if ticker_df.empty:
                normalized[ticker] = ticker_df
                continue

            # Ensure the index is sorted
            ticker_df = ticker_df.sort_index()

            # Find exact match or closest date
            if reference_date in ticker_df.index:
                ref_price = ticker_df.loc[reference_date, 'close']
            else:
                pos = ticker_df.index.searchsorted(reference_date)
                if pos == 0:
                    closest_index = 0
                elif pos == len(ticker_df):
                    closest_index = len(ticker_df) - 1
                else:
                    before = ticker_df.index[pos - 1]
                    after = ticker_df.index[pos]
                    closest_index = pos if after - reference_date < reference_date - before else pos - 1

                ref_price = ticker_df.iloc[closest_index]['close']

            # Create normalized DataFrame with simple ratio normalization (no *100)
            norm_df = ticker_df.copy()
            norm_df['close'] = norm_df['close'] / ref_price
            normalized[ticker] = norm_df

    except Exception as e:
        st.error(f"Error during normalization: {str(e)}")
        return data_dict

    return normalized

def adjust_range_and_interval(start_date: datetime, end_date: datetime, interval: str) -> str:
    """Adjust interval based on date range"""
    date_diff = (end_date - start_date).days

    if interval == "1d" and date_diff > 1825:  # > 5 years
        interval = "1wk"
    elif interval == "1wk" and date_diff < 90:  # < 3 months
        interval = "1d"

    return interval
