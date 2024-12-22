

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
from streamlit_plotly_events import plotly_events

from data_manager import init_db, update_ticker_data, load_data_for_tickers
from utils import normalize_data, adjust_range_and_interval

# Set page configuration
st.set_page_config(layout="wide")

# Initialize the database
init_db()

# Sidebar Controls
st.sidebar.title("Controls")


# Function to robustly load tickers from CSV
def load_tickers(file_path):
    try:
        df = pd.read_csv(file_path)
        if 'ticker' in df.columns:
            return df
        else:
            # Attempt to read without header
            df = pd.read_csv(file_path, header=None, names=["ticker", "name"])
            if 'ticker' in df.columns:
                return df
            else:
                raise ValueError(
                    "Unable to find 'ticker' column in the provided CSV file. "
                    "Please ensure the first column is 'ticker' and the second is 'name'."
                )
    except pd.errors.EmptyDataError:
        st.error("The ticker CSV file is empty. Please provide a valid CSV with ticker data.")
        st.stop()
    except Exception as b:
        st.error(f"Error reading ticker CSV: {b}")
        st.stop()


# Load tickers
tickers_df = load_tickers("config/tickers.csv")
ticker_choices = tickers_df['ticker'].tolist()

# Ticker selection with default options
default_tickers = ["AAPL", "BTC-USD"] if all(t in ticker_choices for t in ["AAPL", "BTC-USD"]) else ticker_choices[:2]

selected_tickers = st.sidebar.multiselect(
    "Select Tickers",
    options=ticker_choices,
    default=default_tickers
)

# Interval selection
interval = st.sidebar.selectbox("Interval", ["1d", "1wk", "1mo"])

# Date range selection
start_date = st.sidebar.date_input("Start Date", datetime.now() - timedelta(days=365))
end_date = st.sidebar.date_input("End Date", datetime.now())

# Adjust interval based on date range
interval = adjust_range_and_interval(start_date, end_date, interval)

# Log scale option
log_scale = st.sidebar.checkbox("Log Scale", False)

# Update data button
refresh_data = st.sidebar.button("Update Data")

# Auto refresh option (placeholder for future implementation)
auto_refresh_interval = st.sidebar.number_input("Auto Refresh (min)", min_value=0, max_value=60, value=0)

# Initialize normalization date in session state
if 'norm_date' not in st.session_state:
    st.session_state['norm_date'] = None

# Update ticker data if requested
if refresh_data:
    update_ticker_data(selected_tickers, interval=interval, force=True)
else:
    update_ticker_data(selected_tickers, interval=interval, force=False)

# Load data for selected tickers
data_loaded = load_data_for_tickers(selected_tickers, start_date, end_date, interval=interval)

# Apply normalization if a reference date is set
if st.session_state['norm_date'] is not None:
    data_normalized = normalize_data(data_loaded, st.session_state['norm_date'])
else:
    data_normalized = data_loaded

# Create Plotly figure with Scattergl for performance
fig = go.Figure()
for ticker, ticker_df in data_normalized.items():
    if not ticker_df.empty:
        fig.add_trace(go.Scattergl(
            x=ticker_df.index,
            y=ticker_df['close'],
            mode='lines',
            name=ticker
        ))

# Update layout
fig.update_layout(
    title="Financial Data",
    xaxis_title="Date",
    yaxis_title="Price" + (" (normalized)" if st.session_state['norm_date'] else ""),
    hovermode="x unified",
    template="plotly_dark"  # Optional: choose a theme
)

# Apply log scale if selected
if log_scale:
    fig.update_yaxes(type='log')

# Display the plot and capture click events
clicked_points = plotly_events(
    fig,
    click_event=True,
    hover_event=False,
    select_event=False,
    key="plot"
)

# Handle click events for normalization
if clicked_points:
    event = clicked_points[0]
    clicked_date_str = event.get('x')
    try:
        clicked_date = pd.to_datetime(clicked_date_str)
        st.session_state['norm_date'] = clicked_date
        st.rerun()
    except Exception as e:
        st.error(f"Failed to parse clicked date: {e}")

# Display normalization reference date
st.write("**Normalization Reference Date:**", st.session_state['norm_date'])
