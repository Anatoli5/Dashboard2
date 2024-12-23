"""Database operations for the application."""

from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
from pathlib import Path

from config.settings import DB_SETTINGS
from .models import Base, TickerData, TickerMetadata


class DatabaseOperations:
    """Handles all database operations."""
    
    def __init__(self):
        """Initialize database connection."""
        # Ensure the parent directory exists
        db_path = Path(DB_SETTINGS['db_path'])
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create database URL
        db_url = f"sqlite:///{db_path}"
        
        # Initialize engine with correct path
        self.engine = create_engine(
            db_url,
            echo=DB_SETTINGS['echo']
        )
        
        # Create tables if they don't exist
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
    
    def save_ticker_data(
        self,
        ticker: str,
        data: pd.DataFrame,
        interval: str,
        provider: str
    ) -> None:
        """Save ticker data to database."""
        session = self.Session()
        try:
            # Delete existing data for this ticker and interval
            session.query(TickerData).filter_by(
                ticker=ticker,
                interval=interval
            ).delete()
            
            # Convert DataFrame to database records
            records = []
            for idx, row in data.iterrows():
                record = TickerData(
                    date=idx,
                    ticker=ticker,
                    interval=interval,
                    open=row['open'],
                    high=row['high'],
                    low=row['low'],
                    close=row['close'],
                    volume=row['volume']
                )
                records.append(record)
            
            # Bulk insert records
            session.bulk_save_objects(records)
            
            # Update metadata
            metadata = session.query(TickerMetadata).filter_by(
                ticker=ticker,
                provider=provider,
                interval=interval
            ).first()
            
            if metadata:
                metadata.last_update = datetime.now()
            else:
                metadata = TickerMetadata(
                    ticker=ticker,
                    provider=provider,
                    interval=interval,
                    last_update=datetime.now()
                )
                session.add(metadata)
            
            session.commit()
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def load_ticker_data(
        self,
        ticker: str,
        interval: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> pd.DataFrame:
        """Load ticker data from database."""
        query = select(TickerData).filter_by(
            ticker=ticker,
            interval=interval
        )
        
        if start_date:
            query = query.filter(TickerData.date >= start_date)
        if end_date:
            query = query.filter(TickerData.date <= end_date)
        
        query = query.order_by(TickerData.date)
        
        with self.engine.connect() as conn:
            df = pd.read_sql(
                query,
                conn,
                index_col='date',
                parse_dates=['date']
            )
        
        return df if not df.empty else pd.DataFrame()
    
    def get_last_update(
        self,
        ticker: str,
        provider: str,
        interval: str
    ) -> Optional[datetime]:
        """Get the last update time for a ticker."""
        session = self.Session()
        try:
            metadata = session.query(TickerMetadata).filter_by(
                ticker=ticker,
                provider=provider,
                interval=interval
            ).first()
            return metadata.last_update if metadata else None
        finally:
            session.close()
    
    def cleanup_old_data(self, days: int = 30) -> None:
        """Remove data older than specified days."""
        session = self.Session()
        try:
            cutoff_date = datetime.now() - pd.Timedelta(days=days)
            session.query(TickerData).filter(
                TickerData.date < cutoff_date
            ).delete()
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close() 