import time
from contextlib import contextmanager
from datetime import datetime
from typing import Generator, Optional, Any, Dict, List, ContextManager
from sqlalchemy.engine import Connection
import pandas as pd
import streamlit as st
import yfinance as yf
from sqlalchemy import create_engine, text, pool
from sqlalchemy.exc import OperationalError

from core.database_utils import DB_PATH, validate_database_structure


class DatabaseManager:
    def __init__(self):
        self.engine = create_engine(
            f"sqlite:///{DB_PATH}",
            echo=False,
            connect_args={
                'timeout': 30,
                'check_same_thread': False
            },
            poolclass=pool.QueuePool,
            pool_size=1,
            max_overflow=0
        )
        self.validate_db()

    @staticmethod
    def validate_db() -> None:
        if not validate_database_structure():
            st.error("Database validation failed")
            raise Exception("Database validation failed")

    @staticmethod
    def fetch_from_yahoo(ticker: str, interval: str = "1d", period: str = "max") -> pd.DataFrame:
        try:
            return yf.download(ticker, period=period, interval=interval, auto_adjust=True, progress=False)
        except Exception as error:
            st.error(f"Error fetching data for {ticker}: {str(error)}")
            return pd.DataFrame()

    @contextmanager
    def get_connection(self, max_retries: int = 3, retry_delay: int = 1) -> ContextManager[Connection]:
        """Context manager for database connections with retry logic"""
        attempt = 0
        last_error: Optional[Exception] = None

        while attempt < max_retries:
            try:
                conn = self.engine.connect()
                try:
                    yield conn
                    return
                finally:
                    conn.close()
            except OperationalError as error:
                last_error = error
                attempt += 1
                if "database is locked" in str(error) and attempt < max_retries:
                    time.sleep(retry_delay)
                else:
                    raise error
            except Exception as error:
                raise error

        if last_error:
            raise last_error
        raise Exception("Failed to connect to database")

    def update_ticker_data(self, tickers: List[str], interval: str = "1d", force: bool = False) -> None:
        now = datetime.utcnow().isoformat()

        if not isinstance(tickers, (list, tuple)):
            raise ValueError("tickers must be a list or tuple")
        if interval not in ["1d", "1wk", "1mo"]:
            raise ValueError("Invalid interval. Must be '1d', '1wk', or '1mo'")

        for ticker in tickers:
            try:
                with self.get_connection() as conn:
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

                    fetched_df.reset_index(inplace=True)
                    fetched_df['ticker'] = ticker
                    fetched_df['interval'] = interval

                    df_to_insert = fetched_df[['ticker', 'Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'interval']]
                    df_to_insert.columns = ['ticker', 'date', 'open', 'high', 'low', 'close', 'volume', 'interval']
                    df_to_insert['date'] = df_to_insert['date'].apply(
                        lambda x: x.isoformat() if hasattr(x, 'isoformat') else str(x)
                    )

                    with conn.begin():
                        conn.execute(
                            text("DELETE FROM ticker_data WHERE ticker=:ticker AND interval=:interval"),
                            {"ticker": ticker, "interval": interval}
                        )

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

                        conn.execute(
                            text("""
                                INSERT OR REPLACE INTO metadata (ticker, interval, last_update)
                                VALUES (:ticker, :interval, :last_update)
                            """),
                            {"ticker": ticker, "interval": interval, "last_update": now}
                        )

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
        data: Dict[str, pd.DataFrame] = {}
        try:
            with self.get_connection() as conn:
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

                    except Exception as error:
                        st.error(f"Error loading data for ticker {ticker}: {str(error)}")
                        data[ticker] = pd.DataFrame()

        except Exception as error:
            st.error(f"Database connection error: {str(error)}")

        return data
