"""Application settings and configurations."""

import os
from pathlib import Path
from typing import Dict
from .themes import COLOR_SCHEMES, DEFAULT_THEME

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Data directory
DATA_DIR = BASE_DIR / 'data'

# Create data directory if it doesn't exist
DATA_DIR.mkdir(exist_ok=True)

# Database settings
DB_SETTINGS = {
    'db_path': str(DATA_DIR / 'market_data.db'),
    'echo': False  # SQL echo for debugging
}

# Data settings
DATA_SETTINGS = {
    'default_provider': 'yahoo',
    'cache_timeout': 300,  # 5 minutes
    'default_interval': '1d',
    'api_keys': {
        'alphavantage': os.getenv('ALPHA_VANTAGE_API_KEY')
    }
}

# Active theme (can be overridden by state management)
ACTIVE_THEME = 'dark'
THEME = COLOR_SCHEMES.get(ACTIVE_THEME, COLOR_SCHEMES[DEFAULT_THEME])

# Ticker lists
TICKER_LISTS: Dict[str, list] = {
    'Crypto': [
        'BTC-USD',
        'ETH-USD',
        'DOGE-USD',
        'ADA-USD',
        'DOT-USD',
        'UNI-USD',
        'LINK-USD',
        'MATIC-USD'
    ],
    'Tech': [
        'AAPL',
        'MSFT',
        'GOOGL',
        'AMZN',
        'META',
        'NVDA',
        'AMD',
        'INTC'
    ],
    'EV & Green': [
        'TSLA',
        'NIO',
        'RIVN',
        'LCID',
        'PLUG',
        'FCEL',
        'ENPH',
        'SEDG'
    ],
    'Finance': [
        'JPM',
        'BAC',
        'GS',
        'MS',
        'V',
        'MA',
        'PYPL',
        'SQ'
    ],
    'Meme': [
        'GME',
        'AMC',
        'BB',
        'BBBY',
        'NOK',
        'WISH',
        'CLOV',
        'PLTR'
    ]
}
