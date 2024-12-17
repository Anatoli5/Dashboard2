# File: core/database_utils.py

import os
import sqlite3
from datetime import datetime

import streamlit as st

DB_PATH = "data.db"


def validate_database_structure():
    """Validate database structure and repair if needed"""
    required_tables = {
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
            'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',  # Changed this line
            'selected_tickers': 'TEXT',
            'start_date': 'TEXT',
            'end_date': 'TEXT',
            'interval': 'TEXT',
            'log_scale': 'INTEGER',
            'norm_date': 'TEXT',
            'last_modified': 'TEXT'
        }
    }

    required_indexes = {
        'ticker_data': [
            'idx_ticker_date',
            'idx_interval'
        ]
    }

    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            existing_tables = {row[0] for row in cursor.fetchall()}

            for table_name, columns in required_tables.items():
                if table_name not in existing_tables:
                    st.warning(f"Missing table {table_name}, creating...")
                    create_table(conn, table_name, columns)
                else:
                    cursor.execute(f"PRAGMA table_info({table_name})")
                    existing_columns = {row[1]: row[2] for row in cursor.fetchall()}

                    for col_name, col_type in columns.items():
                        if col_name not in existing_columns:
                            st.warning(f"Missing column {col_name} in {table_name}, adding...")
                            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type}")
                        elif existing_columns[col_name] != col_type:
                            st.warning(f"Column {col_name} in {table_name} has wrong type, fixing...")
                            fix_column_type(conn, table_name, col_name, col_type)

            cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
            existing_indexes = {row[0] for row in cursor.fetchall()}

            for table_name, indexes in required_indexes.items():
                for index_name in indexes:
                    if index_name not in existing_indexes:
                        st.warning(f"Missing index {index_name}, creating...")
                        if index_name == 'idx_ticker_date':
                            cursor.execute(f"CREATE INDEX {index_name} ON {table_name}(ticker, date)")
                        elif index_name == 'idx_interval':
                            cursor.execute(f"CREATE INDEX {index_name} ON {table_name}(interval)")

            cursor.execute("PRAGMA integrity_check")
            if cursor.fetchone()[0] != "ok":
                raise Exception("Database corruption detected")

            conn.commit()
            return True

    except sqlite3.DatabaseError as e:
        st.error(f"Database error detected: {str(e)}")
        st.warning("Attempting to repair database...")
        repair_database()
        return False
    except Exception as e:
        st.error(f"Unexpected error during database validation: {str(e)}")
        return False


def create_table(conn, table_name, columns):
    """Create a new table with the specified columns"""
    columns_def = ", ".join([f"{name} {type_}" for name, type_ in columns.items()])
    if table_name == 'ticker_data':
        columns_def += ", PRIMARY KEY (ticker, date, interval)"
    conn.execute(f"CREATE TABLE {table_name} ({columns_def})")


def fix_column_type(conn, table_name, column_name, correct_type):
    """Fix column type by creating a new table with correct structure"""
    cursor = conn.cursor()
    try:
        # First check and clean up any existing _old tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (f"{table_name}_old",))
        if cursor.fetchone():
            cursor.execute(f"DROP TABLE {table_name}_old")
            conn.commit()

        # Get the table creation SQL with primary key definition
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        create_sql = cursor.fetchone()[0]

        # Extract primary key definition if it exists
        pk_definition = ""
        if "PRIMARY KEY" in create_sql:
            pk_definition = create_sql[create_sql.find("PRIMARY KEY"):].split(")")[0] + ")"

        # Rename existing table
        cursor.execute(f"ALTER TABLE {table_name} RENAME TO {table_name}_old")

        # Get column info
        cursor.execute(f"PRAGMA table_info({table_name}_old)")
        columns = [(row[1], row[2]) for row in cursor.fetchall()]

        # Create new table with correct column types
        columns_def = ", ".join([
            f"{col} {correct_type if col == column_name else col_type}"
            for col, col_type in columns
        ])

        if pk_definition:
            columns_def += f", {pk_definition}"

        cursor.execute(f"CREATE TABLE {table_name} ({columns_def})")

        # Copy data
        columns_str = ", ".join(col[0] for col in columns)
        cursor.execute(f"INSERT INTO {table_name} SELECT {columns_str} FROM {table_name}_old")

        # Drop old table
        cursor.execute(f"DROP TABLE {table_name}_old")
        conn.commit()
        return True

    except sqlite3.Error as e:
        st.error(f"Error fixing column type: {str(e)}")
        try:
            # Cleanup on error
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
            if not cursor.fetchone():  # If new table wasn't created successfully
                cursor.execute(f"ALTER TABLE {table_name}_old RENAME TO {table_name}")
            conn.commit()
        except sqlite3.Error as cleanup_error:
            st.error(f"Error during cleanup: {str(cleanup_error)}")
        return False


def repair_database():
    """Attempt to repair database by creating a new one and migrating data"""
    backup_path = None
    try:
        # Backup existing database if it exists
        if os.path.exists(DB_PATH):
            backup_path = f"{DB_PATH}.backup.{int(datetime.now().timestamp())}"
            os.rename(DB_PATH, backup_path)
            st.warning(f"Created database backup: {backup_path}")

        # Initialize new database
        with sqlite3.connect(DB_PATH) as conn:
            # Attempt to recover data from backup if it exists
            if backup_path and os.path.exists(backup_path):
                try:
                    with sqlite3.connect(backup_path) as backup_conn:
                        backup_conn.backup(conn)
                    st.success("Successfully recovered data from backup")
                except sqlite3.Error as e:
                    st.error(f"Could not recover data from backup: {str(e)}")

    except sqlite3.Error as e:
        st.error(f"Failed to repair database: {str(e)}")
    except Exception as e:
        st.error(f"Unexpected error during database repair: {str(e)}")
