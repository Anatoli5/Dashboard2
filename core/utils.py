import pandas as pd
import streamlit as st


def normalize_data(data_dict, reference_date):
    """Normalize price data relative to a reference date"""
    if reference_date is None:
        return data_dict

    normalized = {}
    try:
        # Convert reference_date to pandas datetime using proper type checking
        if not isinstance(reference_date, pd.Timestamp):
            try:
                reference_date = pd.to_datetime(reference_date)
            except Exception as e:
                st.error(f"Invalid reference date format: {str(e)}")
                return data_dict

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
                # Get the closest date
                closest_date = ticker_df.index[ticker_df.index.searchsorted(reference_date)]
                ref_price = ticker_df.loc[closest_date, 'close']

            # Create normalized DataFrame
            norm_df = ticker_df.copy()
            norm_df['close'] = (norm_df['close'] / ref_price) * 100  # Convert to percentage
            normalized[ticker] = norm_df

    except Exception as e:
        st.error(f"Error during normalization: {str(e)}")
        return data_dict

    return normalized


def adjust_range_and_interval(start_date, end_date, interval):
    date_diff = (end_date - start_date).days
    # Basic logic: if too large for daily, switch to weekly
    if interval == "1d" and date_diff > 1825:  # > 5 years
        interval = "1wk"
    elif interval == "1wk" and date_diff < 90:
        interval = "1d"
    return interval
