# File: core/data_manager.py

# File: core/data_manager.py

import pandas as pd
from datetime import datetime
import yfinance as yf
import sqlite3
import streamlit as st
from typing import Dict, List
from core.database_utils import DB_PATH


class DatabaseManager:
    def __init__(self):
        self.db_path = DB_PATH
        self.validate_db()

    def validate_db(self) -> None:
        """Ensure database is properly initialized"""
        from core.database_utils import validate_database_structure
        if not validate_database_structure():
            st.error("Database validation failed")
            raise Exception("Database validation failed")

    @staticmethod
    def fetch_from_yahoo(ticker: str, interval: str = "1d", period: str = "max") -> pd.DataFrame:
        """Fetch data from Yahoo Finance"""
        try:
            return yf.download(ticker, period=period, interval=interval, auto_adjust=True, progress=False)
        except Exception as e:
            st.error(f"Error fetching data for {ticker}: {str(e)}")
            return pd.DataFrame()

    def update_ticker_data(self, tickers: List[str], interval: str = "1d", force: bool = False) -> None:
        """Update ticker data using direct SQLite connection"""
        for ticker in tickers:
            try:
                # Fetch new data
                fetched_df = self.fetch_from_yahoo(ticker, interval=interval)
                if fetched_df.empty:
                    st.warning(f"No data available for ticker {ticker}")
                    continue

                # Convert the DataFrame to a list of tuples with actual values
                records = []
                for index, row in fetched_df.iterrows():
                    records.append((
                        ticker,
                        index.strftime('%Y-%m-%d %H:%M:%S'),  # Convert timestamp to string
                        row['Open'].item(),  # Using .item() to get the scalar value
                        row['High'].item(),
                        row['Low'].item(),
                        row['Close'].item(),
                        int(row['Volume'].item()),  # Convert to int after getting scalar value
                        interval
                    ))

                with sqlite3.connect(self.db_path) as conn:
                    # Delete existing data
                    conn.execute("DELETE FROM ticker_data WHERE ticker=? AND interval=?", (ticker, interval))

                    # Insert all records at once
                    conn.executemany("""
                        INSERT INTO ticker_data (ticker, date, open, high, low, close, volume, interval)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, records)

                    # Update metadata
                    conn.execute(
                        "INSERT OR REPLACE INTO metadata (ticker, interval, last_update) VALUES (?, ?, ?)",
                        (ticker, interval, datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))
                    )

                    conn.commit()

            except Exception as error:
                st.error(f"Error processing ticker {ticker}: {str(error)}")
                continue

    def load_data_for_tickers(
            self,
            tickers: List[str],
            start_date: datetime,
            end_date: datetime,
            interval: str = "1d"
    ) -> Dict[str, pd.DataFrame]:
        """Load ticker data using pandas read_sql"""
        data = {}

        try:
            with sqlite3.connect(self.db_path) as conn:
                for ticker in tickers:
                    try:
                        params = [
                            ticker,
                            interval,
                            start_date.isoformat(),
                            end_date.isoformat()
                        ]

                        query = """
                            SELECT date, close 
                            FROM ticker_data
                            WHERE ticker=? 
                            AND interval=?
                            AND date>=? 
                            AND date<=?
                            ORDER BY date ASC
                        """

                        df = pd.read_sql_query(
                            sql=query,
                            con=conn,
                            params=params  # Pass params as a list
                        )

                        if not df.empty:
                            df['date'] = pd.to_datetime(df['date'])
                            df.set_index('date', inplace=True)
                        data[ticker] = df

                    except Exception as error:
                        st.error(f"Error loading data for ticker {ticker}: {str(error)}")
                        data[ticker] = pd.DataFrame()

        except Exception as error:
            st.error(f"Database connection error: {str(error)}")

        return data
