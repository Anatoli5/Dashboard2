import streamlit as st

from config.loader import ConfigLoader
from config.settings import Settings
from core.data_manager import init_db, update_ticker_data, load_data_for_tickers
from core.utils import normalize_data, adjust_range_and_interval
from ui.layout import DashboardLayout
from ui.sidebar import SidebarControls
from visualization.charts import ChartManager


def main():
    # Initialize
    DashboardLayout.setup_page()
    init_db()

    # Load configuration
    tickers_df = ConfigLoader.load_tickers(Settings.TICKERS_FILE)
    ticker_choices = tickers_df['ticker'].tolist()
    default_tickers = ["AAPL", "BTC-USD"] if all(
        t in ticker_choices for t in ["AAPL", "BTC-USD"]
    ) else ticker_choices[:2]

    # Render sidebar controls
    selected_tickers = SidebarControls.render_ticker_selection(
        ticker_choices,
        default_tickers
    )
    start_date, end_date = SidebarControls.render_date_controls()
    interval, log_scale = SidebarControls.render_chart_controls()

    # Process data
    interval = adjust_range_and_interval(start_date, end_date, interval)
    update_ticker_data(selected_tickers, interval=interval)
    data_loaded = load_data_for_tickers(
        selected_tickers,
        start_date,
        end_date,
        interval=interval
    )

    # Create and display visualization
    if 'norm_date' not in st.session_state:
        st.session_state['norm_date'] = None

    data_normalized = normalize_data(
        data_loaded,
        st.session_state['norm_date']
    )

    fig = ChartManager.create_price_chart(data_normalized, log_scale)
    DashboardLayout.render_main_area(fig)


if __name__ == "__main__":
    main()
