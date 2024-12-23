"""Database models for the application."""

from sqlalchemy import Column, String, Float, DateTime, Index
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class TickerData(Base):
    """Model for storing ticker price data."""
    
    __tablename__ = 'ticker_data'
    
    # Primary key is composite of date and ticker
    date = Column(DateTime, primary_key=True)
    ticker = Column(String, primary_key=True)
    interval = Column(String, primary_key=True)
    
    # OHLCV data
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)
    
    # Create indexes for common queries
    __table_args__ = (
        Index('idx_ticker_date', 'ticker', 'date'),
        Index('idx_date', 'date'),
        Index('idx_ticker_interval', 'ticker', 'interval')
    )


class TickerMetadata(Base):
    """Model for storing ticker metadata."""
    
    __tablename__ = 'ticker_metadata'
    
    ticker = Column(String, primary_key=True)
    provider = Column(String, primary_key=True)
    last_update = Column(DateTime)
    interval = Column(String, primary_key=True)
    
    # Create index for update queries
    __table_args__ = (
        Index('idx_last_update', 'last_update'),
    ) 