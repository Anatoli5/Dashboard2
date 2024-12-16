from typing import List, Dict, Optional
import pandas as pd
from datetime import datetime, date, timedelta
from sqlalchemy import create_engine, text
# from sqlalchemy.engine import Row
from config.settings import DATABASE_PATH
from providers.base_provider import BaseProvider


class DatabaseHandler:
    """
    Handles database operations for ticker data.
    """

    def __init__(
            self,
            db_path: str = DATABASE_PATH,
            data_provider: Optional[BaseProvider] = None
    ) -> None:
        """
        Initializes the DatabaseHandler.

        Args:
            db_path (str): Path to the SQLite database file.
            data_provider (Optional[BaseProvider]): An instance of a data provider implementing BaseProvider.
        """
        self.db_path = db_path
        self.engine = create_engine(f"sqlite:///{self.db_path}", echo=False, future=True)
        self.data_provider = data_provider
        self.init_db()

    def init_db(self) -> None:
        """
        Initializes the database by creating required tables if they do not exist.
        """
        with self.engine.connect() as conn:
            # Create tables if they do not exist
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS ticker_data (
                    ticker TEXT,
                    date TEXT,
                    open REAL,
                    high REAL,
                    low REAL,
                    close REAL,
                    volume REAL,
                    interval TEXT,
                    PRIMARY KEY (ticker, date, interval)
                )
            """))
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS metadata (
                    ticker TEXT,
                    interval TEXT,
                    last_update TEXT,
                    last_date TEXT,
                    PRIMARY KEY (ticker, interval)
                )
            """))
            conn.commit()

    def update_ticker_data(
            self,
            tickers: List[str],
            interval: str = "1d",
            force: bool = False
    ) -> None:
        if self.data_provider is None:
            raise ValueError("Data provider must be provided.")

        now = datetime.utcnow().isoformat()
        with self.engine.begin() as conn:
            for ticker in tickers:
                # Fetch the last update date from metadata table
                result = conn.execute(
                    text("""
                        SELECT last_update, last_date FROM metadata
                        WHERE ticker=:ticker AND interval=:interval
                    """),
                    {"ticker": ticker, "interval": interval}
                )
                row = result.mappings().fetchone()
                last_date = None if row is None else row['last_date']

                # Determine fetch start date
                if force or last_date is None:
                    start_date = None  # Fetch all available data
                else:
                    start_date = (datetime.fromisoformat(last_date) + timedelta(days=1)).date()

                # Fetch new data
                fetched_df = self.data_provider.fetch_data(
                    ticker,
                    start_date=start_date,
                    interval=interval
                )

                if not fetched_df.empty:
                    fetched_df.reset_index(inplace=True)
                    fetched_df['ticker'] = ticker
                    fetched_df['interval'] = interval

                    df_to_insert = fetched_df[[
                        'ticker', 'Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'interval'
                    ]]
                    df_to_insert.columns = [
                        'ticker', 'date', 'open', 'high', 'low', 'close', 'volume', 'interval'
                    ]

                    # Convert dates to ISO format
                    df_to_insert['date'] = df_to_insert['date'].apply(lambda x: x.isoformat())

                    # Insert new data into the database
                    insert_query = text("""
                        INSERT OR IGNORE INTO ticker_data
                        (ticker, date, open, high, low, close, volume, interval)
                        VALUES (:ticker, :date, :open, :high, :low, :close, :volume, :interval)
                    """)
                    data_to_insert = df_to_insert.to_dict(orient='records')
                    conn.execute(insert_query, data_to_insert)

                    # Update metadata
                    last_date_in_data = df_to_insert['date'].max()
                    conn.execute(text("""
                        REPLACE INTO metadata
                        (ticker, interval, last_update, last_date)
                        VALUES (:ticker, :interval, :last_update, :last_date)
                    """), {
                        "ticker": ticker,
                        "interval": interval,
                        "last_update": now,
                        "last_date": last_date_in_data
                    })

    def load_data_for_tickers(
            self,
            tickers: List[str],
            start_date: date,
            end_date: date,
            interval: str = "1d"
    ) -> Dict[str, pd.DataFrame]:
        """
        Loads data for the specified tickers from the database.

        Args:
            tickers (List[str]): List of ticker symbols to load data for.
            start_date (date): The start date for data retrieval.
            end_date (date): The end date for data retrieval.
            interval (str): Data interval (e.g., '1d', '1wk', '1mo').

        Returns:
            Dict[str, pd.DataFrame]: Dictionary of DataFrames keyed by ticker symbol.
        """
        data = {}
        with self.engine.connect() as conn:
            for ticker in tickers:
                query = text("""
                    SELECT date, close FROM ticker_data
                    WHERE ticker=:ticker AND interval=:interval
                      AND date BETWEEN :start_date AND :end_date
                    ORDER BY date ASC
                """)
                params = {
                    "ticker": ticker,
                    "interval": interval,
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                }
                fetched_df = pd.read_sql_query(query, conn, params=params)

                if not fetched_df.empty:
                    fetched_df['date'] = pd.to_datetime(fetched_df['date'])
                    fetched_df.set_index('date', inplace=True)
                data[ticker] = fetched_df

        return data
