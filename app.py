from typing import List
import streamlit as st
from dashboard.layout import create_dashboard
from dashboard.visualization import process_and_visualize_data  # Add this import
from config.settings import MAX_DATE_RANGE_DAYS, TICKERS_CSV_PATH, DATA_PROVIDER
from database.handler import DatabaseHandler
from utils.data_processor import DataProcessor
from providers.yahoo_finance_provider import YahooFinanceProvider
from providers.alpha_vantage_provider import AlphaVantageProvider


def main() -> None:
    """Main function to run the Streamlit app."""
    st.set_page_config(layout="wide")
    st.sidebar.title("Controls")

    # Initialize necessary components
    data_provider = get_data_provider()
    db_handler = DatabaseHandler(data_provider=data_provider)
    data_processor = DataProcessor()

    tickers = load_tickers(TICKERS_CSV_PATH)

    # Create dashboard layout and get user inputs
    user_inputs = create_dashboard(tickers, MAX_DATE_RANGE_DAYS)

    if user_inputs.selected_tickers:
        # Update and load data
        try:
            db_handler.update_ticker_data(
                user_inputs.selected_tickers,
                interval=user_inputs.interval,
                force=user_inputs.refresh_data
            )
            data_loaded = db_handler.load_data_for_tickers(
                user_inputs.selected_tickers,
                user_inputs.start_date,
                user_inputs.end_date,
                interval=user_inputs.interval
            )
            # Process and visualize data
            process_and_visualize_data(
                data_loaded,
                user_inputs,
                data_processor
            )
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please select at least one ticker to display data.")


@st.cache_data
def load_tickers(file_path: str) -> List[str]:
    """Loads tickers from a CSV file."""
    import pandas as pd
    try:
        df = pd.read_csv(file_path)
        if 'ticker' in df.columns:
            return df['ticker'].tolist()
        else:
            raise ValueError("CSV file must contain 'ticker' column.")
    except Exception as e:
        st.error(f"Error reading ticker CSV: {e}")
        st.stop()


def get_data_provider():
    """Returns the data provider instance based on configuration."""
    if DATA_PROVIDER == 'YahooFinance':
        return YahooFinanceProvider()
    elif DATA_PROVIDER == 'AlphaVantage':
        return AlphaVantageProvider()
    else:
        st.error(f"Unsupported data provider: {DATA_PROVIDER}")
        st.stop()


if __name__ == '__main__':
    main()
