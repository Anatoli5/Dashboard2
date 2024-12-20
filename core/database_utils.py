# File: core/database_utils.py

import os
import sqlite3
import streamlit as st
from sqlalchemy import create_engine, text

DB_PATH = "data.db"

def validate_database_structure() -> bool:
    """Validate and initialize database structure if needed"""
    if not os.path.exists(DB_PATH):
        return create_database()
    
    try:
        engine = create_engine(f"sqlite:///{DB_PATH}", echo=False, future=True)
        with engine.connect() as conn:
            # Check required tables
            tables = {
                'ticker_data': {
                    'ticker': 'TEXT',
                    'date': 'TEXT',
                    'open': 'REAL',
                    'high': 'REAL',
                    'low': 'REAL',
                    'close': 'REAL',
                    'volume': 'REAL',
                    'interval': 'TEXT'
                },
                'metadata': {
                    'ticker': 'TEXT',
                    'interval': 'TEXT',
                    'last_update': 'TEXT'
                },
                'app_state': {
                    'id': 'INTEGER PRIMARY KEY',
                    'selected_tickers': 'TEXT',
                    'start_date': 'TEXT',
                    'end_date': 'TEXT',
                    'interval': 'TEXT',
                    'log_scale': 'INTEGER',
                    'norm_date': 'TEXT',
                    'last_modified': 'TEXT'
                }
            }

            for table_name, columns in tables.items():
                create_table_if_not_exists(conn, table_name, columns)

        return True

    except Exception as e:
        st.error(f"Database validation error: {str(e)}")
        return False

def create_database() -> bool:
    """Create a new database with required tables"""
    try:
        engine = create_engine(f"sqlite:///{DB_PATH}", echo=False, future=True)
        with engine.connect() as conn:
            # Create ticker_data table
            conn.execute(text("""
                CREATE TABLE ticker_data (
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

            # Create metadata table
            conn.execute(text("""
                CREATE TABLE metadata (
                    ticker TEXT,
                    interval TEXT,
                    last_update TEXT,
                    PRIMARY KEY (ticker, interval)
                )
            """))

            # Create app_state table
            conn.execute(text("""
                CREATE TABLE app_state (
                    id INTEGER PRIMARY KEY,
                    selected_tickers TEXT,
                    start_date TEXT,
                    end_date TEXT,
                    interval TEXT,
                    log_scale INTEGER,
                    norm_date TEXT,
                    last_modified TEXT
                )
            """))

            conn.commit()
        return True

    except Exception as e:
        st.error(f"Database creation error: {str(e)}")
        return False

def create_table_if_not_exists(conn, table_name: str, columns: dict) -> None:
    """Create a table if it doesn't exist"""
    columns_def = ", ".join([f"{name} {type_}" for name, type_ in columns.items()])
    conn.execute(text(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_def})"))