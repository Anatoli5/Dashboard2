# File: core/utils.py

import pandas as pd
from datetime import datetime
import streamlit as st
from typing import Dict


def normalize_data(data_dict, norm_date=None):
    """
    Normalize data for comparison.
    
    Args:
        data_dict (dict): Dictionary of DataFrames with price data
        norm_date (datetime.date, optional): Date to normalize to. If None, uses first date
        
    Returns:
        dict: Dictionary of normalized DataFrames
    """
    if not data_dict or all(df.empty for df in data_dict.values()):
        return data_dict
        
    # Use existing data without copying if no normalization needed
    if not norm_date:
        return data_dict
        
    normalized = {}
    for ticker, df in data_dict.items():
        if df.empty:
            normalized[ticker] = df
            continue
            
        try:
            # Find normalization value
            norm_date_ts = pd.Timestamp(norm_date)
            if norm_date_ts not in df.index:
                # If exact date not found, use nearest date
                nearest_date = min(df.index, key=lambda x: abs(x - norm_date_ts))
                st.info(f"Using nearest date {nearest_date.date()} for normalization of {ticker}")
                norm_date_ts = nearest_date
            
            # Only normalize the close column which is used for display
            df_norm = df.copy()
            norm_value = df.loc[norm_date_ts, 'close']
            df_norm['close'] = (df['close'] / norm_value) * 100
                    
            normalized[ticker] = df_norm
            
        except Exception as e:
            st.error(f"Error normalizing {ticker}: {str(e)}")
            normalized[ticker] = df
            
    return normalized

def adjust_range_and_interval(start_date: datetime, end_date: datetime, interval: str) -> str:
    """Adjust interval based on date range"""
    date_diff = (end_date - start_date).days

    if interval == "1d" and date_diff > 1825:  # > 5 years
        interval = "1wk"
    elif interval == "1wk" and date_diff < 90:  # < 3 months
        interval = "1d"

    return interval
