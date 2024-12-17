# File: core/data_manager.py

import pandas as pd
from datetime import datetime
import yfinance as yf
from sqlalchemy import create_engine, text
import streamlit as st

from core.database_utils import DB_PATH, validate_database_structure


class DatabaseManager:
    def __init__(self):
        self.engine = create_engine(f"sqlite:///{DB_PATH}", echo=False, future=True)
        self.validate_db()

    @staticmethod
    def validate_db():
        """Ensure database is properly initialized"""
        if not validate_database_structure():
            st.error("Database validation failed")
            raise Exception("Database validation failed")

    @staticmethod
    def fetch_from_yahoo(ticker, interval="1d", period="max"):
        """Fetch data from Yahoo Finance"""
        try:
            return yf.download(ticker, period=period, interval=interval, auto_adjust=True, progress=False)
        except Exception as e:
            st.error(f"Error fetching data for {ticker}: {str(e)}")
            return pd.DataFrame()

    # File: core/data_manager.py
    # STATUS: PARTIAL UPDATE
    # Replace the update_ticker_data method in DatabaseManager class

    def update_ticker_data(self, tickers, interval="1d", force=False):
        """Update ticker data with proper transaction handling"""
        now = datetime.utcnow().isoformat()

        if not isinstance(tickers, (list, tuple)):
            raise ValueError("tickers must be a list or tuple")
        if interval not in ["1d", "1wk", "1mo"]:
            raise ValueError("Invalid interval. Must be '1d', '1wk', or '1mo'")

        for ticker in tickers:
            # Create a new engine and connection for each ticker
            with create_engine(f"sqlite:///{DB_PATH}", echo=False, future=True).connect() as conn:
                try:
                    # Check last update time if not forced
                    if not force:
                        result = conn.execute(
                            text("SELECT last_update FROM metadata WHERE ticker=:ticker AND interval=:interval"),
                            {"ticker": ticker, "interval": interval}
                        )
                        row = result.fetchone()
                        if row and (datetime.utcnow() - datetime.fromisoformat(row[0])).total_seconds() < 3600:
                            continue

                    fetched_df = self.fetch_from_yahoo(ticker, interval=interval)

                    if fetched_df.empty:
                        st.warning(f"No data available for ticker {ticker}")
                        continue

                    if fetched_df.isnull().values.any():
                        fetched_df = fetched_df.fillna(method='ffill')

                    if not all(col in fetched_df.columns for col in ['Open', 'High', 'Low', 'Close', 'Volume']):
                        st.error(f"Missing required columns for ticker {ticker}")
                        continue

                    # Prepare data for insertion
                    fetched_df.reset_index(inplace=True)
                    fetched_df['ticker'] = ticker
                    fetched_df['interval'] = interval

                    df_to_insert = fetched_df[['ticker', 'Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'interval']]
                    df_to_insert.columns = ['ticker', 'date', 'open', 'high', 'low', 'close', 'volume', 'interval']
                    df_to_insert['date'] = df_to_insert['date'].apply(
                        lambda x: x.isoformat() if hasattr(x, 'isoformat') else str(x)
                    )

                    # Execute all operations in a single transaction
                    with conn.begin():
                        # Delete existing data
                        conn.execute(
                            text("DELETE FROM ticker_data WHERE ticker=:ticker AND interval=:interval"),
                            {"ticker": ticker, "interval": interval}
                        )

                        # Insert new data in chunks
                        chunk_size = 500
                        records = df_to_insert.to_dict(orient='records')
                        for i in range(0, len(records), chunk_size):
                            chunk = records[i:i + chunk_size]
                            conn.execute(
                                text("""
                                    INSERT INTO ticker_data 
                                    (ticker, date, open, high, low, close, volume, interval)
                                    VALUES 
                                    (:ticker, :date, :open, :high, :low, :close, :volume, :interval)
                                """),
                                chunk
                            )

                        # Update metadata
                        conn.execute(
                            text("""
                                INSERT OR REPLACE INTO metadata (ticker, interval, last_update)
                                VALUES (:ticker, :interval, :last_update)
                            """),
                            {"ticker": ticker, "interval": interval, "last_update": now}
                        )

                except Exception as e:
                    st.error(f"Error processing ticker {ticker}: {str(e)}")
                    continue

    def load_data_for_tickers(self, tickers, start_date, end_date, interval="1d"):
        """Load ticker data with proper error handling"""
        data = {}
        try:
            with self.engine.connect() as conn:
                for ticker in tickers:
                    try:
                        query = text("""
                            SELECT date, close 
                            FROM ticker_data
                            WHERE ticker=:ticker 
                            AND interval=:interval 
                            AND date>=:start_date 
                            AND date<=:end_date
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
                            fetched_df['date'] = pd.to_datetime(fetched_df['date'], errors='coerce')
                            fetched_df.dropna(subset=['date'], inplace=True)
                            fetched_df.set_index('date', inplace=True)
                        data[ticker] = fetched_df

                    except Exception as e:
                        st.error(f"Error loading data for ticker {ticker}: {str(e)}")
                        data[ticker] = pd.DataFrame()

        except Exception as e:
            st.error(f"Database connection error: {str(e)}")

        return data
