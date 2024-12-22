# File: core/data_manager.py

import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine, text
import streamlit as st
from typing import Dict, List
from core.database_utils import DB_PATH
from core.data_providers import get_data_provider, DataProvider


class DatabaseManager:
    def __init__(self, data_provider: str = "yahoo", api_key: str = None):
        self.engine = create_engine(f"sqlite:///{DB_PATH}", 
                                  echo=False, 
                                  future=True,
                                  pool_pre_ping=True,
                                  pool_recycle=3600)
        self.data_provider = get_data_provider(data_provider, api_key)
        self.validate_db()

    def validate_db(self) -> None:
        """Ensure database is properly initialized"""
        from core.database_utils import validate_database_structure
        if not validate_database_structure():
            st.error("Database validation failed")
            raise Exception("Database validation failed")

    def update_ticker_data(self, tickers: List[str], interval: str = "1d", force: bool = False) -> None:
        """Update ticker data using a new connection for each ticker"""
        now = datetime.utcnow().isoformat()
        successful_updates = []
        failed_updates = []
        
        for ticker in tickers:
            try:
                # Check if update is needed
                with self.engine.begin() as conn:
                    result = conn.execute(
                        text("SELECT last_update FROM metadata WHERE ticker=:ticker AND interval=:interval"),
                        {"ticker": ticker, "interval": interval}
                    ).fetchone()
                    
                    if not force and result and (datetime.utcnow() - datetime.fromisoformat(result[0])).total_seconds() < 3600:
                        successful_updates.append(ticker)
                        continue

                # Fetch new data using the selected provider
                fetched_df = self.data_provider.fetch_data(ticker, interval=interval)
                if fetched_df.empty:
                    failed_updates.append(ticker)
                    continue

                # Process and save data
                with self.engine.begin() as conn:
                    fetched_df.reset_index(inplace=True)
                    records = []
                    for _, row in fetched_df.iterrows():
                        date_val = row['Date']
                        if isinstance(date_val, pd.Series):
                            date_val = date_val.iloc[0]
                        
                        records.append({
                            'ticker': ticker,
                            'date': date_val.isoformat(),
                            'open': float(row['Open'].iloc[0]) if isinstance(row['Open'], pd.Series) else float(row['Open']),
                            'high': float(row['High'].iloc[0]) if isinstance(row['High'], pd.Series) else float(row['High']),
                            'low': float(row['Low'].iloc[0]) if isinstance(row['Low'], pd.Series) else float(row['Low']),
                            'close': float(row['Close'].iloc[0]) if isinstance(row['Close'], pd.Series) else float(row['Close']),
                            'volume': float(row['Volume'].iloc[0]) if isinstance(row['Volume'], pd.Series) else float(row['Volume']),
                            'interval': interval
                        })

                    # Update database in a single transaction
                    conn.execute(
                        text("DELETE FROM ticker_data WHERE ticker=:ticker AND interval=:interval"),
                        {"ticker": ticker, "interval": interval}
                    )

                    if records:
                        conn.execute(
                            text("""
                                INSERT INTO ticker_data 
                                (ticker, date, open, high, low, close, volume, interval)
                                VALUES 
                                (:ticker, :date, :open, :high, :low, :close, :volume, :interval)
                            """),
                            records
                        )

                        conn.execute(
                            text("""
                                INSERT OR REPLACE INTO metadata (ticker, interval, last_update)
                                VALUES (:ticker, :interval, :last_update)
                            """),
                            {"ticker": ticker, "interval": interval, "last_update": now}
                        )
                        
                    successful_updates.append(ticker)

            except Exception as e:
                st.error(f"Error processing {ticker}: {str(e)}")
                failed_updates.append(ticker)
                continue

        # Show summary of updates
        if successful_updates:
            st.success(f"Successfully updated: {', '.join(successful_updates)}")
        if failed_updates:
            st.warning(f"Failed to update: {', '.join(failed_updates)}")

    def load_data_for_tickers(
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