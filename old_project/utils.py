def normalize_data(data_dict, reference_date):
    normalized = {}
    for ticker, ticker_df in data_dict.items():
        if ticker_df.empty:
            normalized[ticker] = ticker_df
            continue

        # Ensure the index is sorted
        ticker_df = ticker_df.sort_index()

        # Find the position where the reference_date would fit in the sorted index
        pos = ticker_df.index.searchsorted(reference_date)

        # Determine the closest index
        if pos == 0:  # Reference date is before the first date in the index
            closest_index = 0
        elif pos == len(ticker_df):  # Reference date is after the last date in the index
            closest_index = len(ticker_df) - 1
        else:
            before = ticker_df.index[pos - 1]
            after = ticker_df.index[pos]
            closest_index = pos if after - reference_date < reference_date - before else pos - 1

        # Get the reference price and normalize the DataFrame
        ref_price = ticker_df.iloc[closest_index]['close']
        norm_df = ticker_df.copy()
        norm_df['close'] = norm_df['close'] / ref_price
        normalized[ticker] = norm_df

    return normalized


def adjust_range_and_interval(start_date, end_date, interval):
    date_diff = (end_date - start_date).days
    # Basic logic: if too large for daily, switch to weekly
    if interval == "1d" and date_diff > 1825:  # > 5 years
        interval = "1wk"
    elif interval == "1wk" and date_diff < 90:
        interval = "1d"
    return interval
