# File: core/data_manager.py

import pandas as pd
from datetime import datetime
import yfinance as yf
from sqlalchemy import create_engine, text
import streamlit as st
from typing import Dict, List
from core.database_utils import DB_PATH
from typing import Dict, List
from core.database_utils import DB_PATH


class DatabaseManager:
    def __init__(self):
        self.engine = create_engine(f"sqlite:///{DB_PATH}", echo=False, future=True)
        self.validate_db()

    def validate_db(self) -> None:
        """Ensure database is properly initialized"""
        from core.database_utils import validate_database_structure
    def validate_db(self) -> None:
        """Ensure database is properly initialized"""
        from core.database_utils import validate_database_structure
        if not validate_database_structure():
            st.error("Database validation failed")
            raise Exception("Database validation failed")

    @staticmethod
    def fetch_from_yahoo(ticker: str, interval: str = "1d", period: str = "max") -> pd.DataFrame:
        """Fetch data from Yahoo Finance"""
        """Fetch data from Yahoo Finance"""
        try:
            return yf.download(ticker, period=period, interval=interval, auto_adjust=True, progress=False)
        except Exception as e:
            st.error(f"Error fetching data for {ticker}: {str(e)}")
        except Exception as e:
            st.error(f"Error fetching data for {ticker}: {str(e)}")
            return pd.DataFrame()

    def update_ticker_data(self, tickers: List[str], interval: str = "1d", force: bool = False) -> None:
        """Update ticker data with proper transaction handling"""
        now = datetime.utcnow().isoformat()

        with self.engine.connect() as conn:
            for ticker in tickers:
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

                    # Prepare data for insertion
                    fetched_df.reset_index(inplace=True)
                    fetched_df['ticker'] = ticker
                    fetched_df['interval'] = interval

                    df_to_insert = fetched_df[['ticker', 'Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'interval']]
                    df_to_insert.columns = ['ticker', 'date', 'open', 'high', 'low', 'close', 'volume', 'interval']
                    df_to_insert['date'] = df_to_insert['date'].apply(lambda x: x.isoformat())

                    # Execute operations in a transaction
                    with conn.begin():
                        # Delete existing data
                        conn.execute(
                            text("DELETE FROM ticker_data WHERE ticker=:ticker AND interval=:interval"),
                            {"ticker": ticker, "interval": interval}
                        )

                        # Insert new data
                        insert_query = text("""
                            INSERT INTO ticker_data 
                            (ticker, date, open, high, low, close, volume, interval)
                            VALUES 
                            (:ticker, :date, :open, :high, :low, :close, :volume, :interval)
                        """)
                        conn.execute(insert_query, df_to_insert.to_dict(orient='records'))

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

    def load_data_for_tickers(
            self,
            tickers: List[str],
            start_date: datetime,
            end_date: datetime,
            interval: str = "1d"
            self,
            tickers: List[str],
            start_date: datetime,
            end_date: datetime,
            interval: str = "1d"
    ) -> Dict[str, pd.DataFrame]:
        """Load ticker data efficiently"""
        data = {}
        
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

                    df = pd.read_sql_query(query, conn, params=params)
                    if not df.empty:
                        df['date'] = pd.to_datetime(df['date'])
                        df.set_index('date', inplace=True)
                    data[ticker] = df

                except Exception as e:
                    st.error(f"Error loading data for ticker {ticker}: {str(e)}")
                    data[ticker] = pd.DataFrame()

        return data