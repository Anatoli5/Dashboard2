import pandas as pd
import os
from datetime import datetime
import yfinance as yf
from sqlalchemy import create_engine, text

DB_PATH = "data.db"
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False, future=True)


def init_db():
    if not os.path.exists(DB_PATH):
        with engine.connect() as conn:
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
                    PRIMARY KEY (ticker, interval)
                )
            """))
            conn.commit()


def fetch_from_yahoo(ticker, interval="1d", period="max"):
    fetched_df = yf.download(ticker, period=period, interval=interval, auto_adjust=True, progress=False)
    return fetched_df


def update_ticker_data(tickers, interval="1d", force=False):
    now = datetime.utcnow().isoformat()
    with engine.connect() as conn:
        for ticker in tickers:
            result = conn.execute(
                text("SELECT last_update FROM metadata WHERE ticker=:ticker AND interval=:interval"),
                {"ticker": ticker, "interval": interval}
            )
            row = result.fetchone()
            last_update = None if row is None else row[0]

            # Update if forced or no previous data
            if force or last_update is None:
                fetched_df = fetch_from_yahoo(ticker, interval=interval)
                if not fetched_df.empty:
                    fetched_df.reset_index(inplace=True)
                    fetched_df['ticker'] = ticker
                    fetched_df['interval'] = interval

                    df_to_insert = fetched_df[['ticker', 'Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'interval']]
                    df_to_insert.columns = ['ticker', 'date', 'open', 'high', 'low', 'close', 'volume', 'interval']

                    # Convert Timestamp to string for SQLite insertion
                    # This ensures no 'Timestamp' type is passed to SQLite.
                    df_to_insert['date'] = df_to_insert['date'].apply(
                        lambda x: x.isoformat() if hasattr(x, 'isoformat') else str(x))

                    # Remove old data for this ticker & interval
                    conn.execute(
                        text("DELETE FROM ticker_data WHERE ticker=:ticker AND interval=:interval"),
                        {"ticker": ticker, "interval": interval}
                    )

                    # Insert new data
                    insert_query = text("""
                        INSERT INTO ticker_data (ticker, date, open, high, low, close, volume, interval)
                        VALUES (:ticker, :date, :open, :high, :low, :close, :volume, :interval)
                    """)
                    data_to_insert_dict = df_to_insert.to_dict(orient='records')
                    conn.execute(insert_query, data_to_insert_dict)

                    # Update metadata
                    conn.execute(text("""
                        REPLACE INTO metadata (ticker, interval, last_update)
                        VALUES (:ticker, :interval, :last_update)
                    """), {"ticker": ticker, "interval": interval, "last_update": now})
        conn.commit()


def load_data_for_tickers(tickers, start_date, end_date, interval="1d"):
    data = {}
    with engine.connect() as conn:
        for ticker in tickers:
            query = text("""
                SELECT date, close FROM ticker_data
                WHERE ticker=:ticker AND interval=:interval AND date>=:start_date AND date<=:end_date
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
                # Convert the date column back to datetime
                fetched_df['date'] = pd.to_datetime(fetched_df['date'], errors='coerce')
                fetched_df.dropna(subset=['date'], inplace=True)
                fetched_df.set_index('date', inplace=True)
            data[ticker] = fetched_df
    return data
