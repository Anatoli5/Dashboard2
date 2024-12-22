# File: core/data_manager.py

import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine, text
import streamlit as st
from typing import Dict, List, Optional
from core.database_utils import DB_PATH
from core.data_providers import get_data_provider, DataProvider


class DatabaseManager:
    """Manages database operations for ticker data"""
    
    def __init__(self, data_provider: str = "yahoo", api_key: Optional[str] = None):
        """Initialize database manager"""
        self.engine = create_engine(f'sqlite:///{DB_PATH}')
        self.provider = get_data_provider(data_provider, api_key)
        
    def update_ticker_data(
            self,
            tickers: List[str],
            interval: str = "1d",
            force: bool = False
    ) -> None:
        """Update data for given tickers"""
        with self.engine.connect() as conn:
            for ticker in tickers:
                try:
                    # Check if we need to update
                    if not force:
                        query = text("""
                            SELECT MAX(date) as last_date 
                            FROM ticker_data 
                            WHERE ticker=:ticker 
                            AND interval=:interval
                        """)
                        result = conn.execute(query, {"ticker": ticker, "interval": interval})
                        row = result.fetchone()
                        
                        if row and row[0]:
                            last_date = pd.to_datetime(row[0])
                            if last_date.date() >= datetime.now().date():
                                continue
                    
                    # Fetch new data
                    df = self.provider.fetch_data(ticker, interval)
                    if df.empty:
                        continue
                    
                    # Ensure column names are lowercase for storage
                    df.columns = df.columns.str.lower()
                    
                    # Prepare data for insertion
                    df = df.reset_index()
                    df['ticker'] = ticker
                    df['interval'] = interval
                    
                    # Delete existing data for this ticker and interval
                    delete_query = text("""
                        DELETE FROM ticker_data 
                        WHERE ticker=:ticker 
                        AND interval=:interval
                    """)
                    conn.execute(delete_query, {"ticker": ticker, "interval": interval})
                    
                    # Insert new data
                    df.to_sql('ticker_data', conn, if_exists='append', index=False)
                    
                except Exception as e:
                    st.error(f"Error updating data for ticker {ticker}: {str(e)}")
    
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
                        SELECT date, open, high, low, close, volume 
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
                        # Keep column names lowercase for consistency
                        df.columns = df.columns.str.lower()
                    data[ticker] = df

                except Exception as e:
                    st.error(f"Error loading data for ticker {ticker}: {str(e)}")
                    data[ticker] = pd.DataFrame()

        return data