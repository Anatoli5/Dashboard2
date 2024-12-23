from pathlib import Path


class Settings:
    DB_PATH: str = "data.db"
    TICKERS_FILE: Path = Path("files/crypto_tickers.csv")
    DEFAULT_INTERVAL: str = "1d"
    DEFAULT_PERIOD: str = "max"

    @staticmethod
    def get_db_url() -> str:
        return f"sqlite:///{Settings.DB_PATH}"

"""Application configuration settings."""

import os
from pathlib import Path

# Create base paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data'
DATA_DIR.mkdir(exist_ok=True)  # Create data directory if it doesn't exist

# App configuration
APP_CONFIG = {
    'title': 'Financial Dashboard',
    'update_title': None,  # Remove "Updating..." from title
    'assets_folder': BASE_DIR / 'frontend' / 'assets',
    'include_assets_files': True,
    'assets_external_path': '/assets/',
    'serve_locally': True,
}

# Data settings
DATA_SETTINGS = {
    'default_provider': 'yahoo',
    'cache_timeout': 300,  # 5 minutes
    'default_interval': '1d',
}

# Database settings
DB_SETTINGS = {
    'db_path': str(DATA_DIR / 'market_data.db'),
    'echo': False,  # SQL echo for debugging
}

# Theme settings
THEME = {
    'dark': {
        'bg_color': '#0E1117',
        'plot_bg_color': '#0E1117',
        'grid_color': '#333333',
        'text_color': '#FAFAFA',
        'axis_color': '#666666',
        'watermark_color': 'rgba(255, 255, 255, 0.1)',
        'line_color': '#444444',
        'hover_bg': 'rgba(14, 17, 23, 0.9)'
    },
    'light': {
        'bg_color': '#FFFFFF',
        'plot_bg_color': '#FFFFFF',
        'grid_color': '#E5E5E5',
        'text_color': '#262730',
        'axis_color': '#666666',
        'watermark_color': 'rgba(0, 0, 0, 0.1)',
        'line_color': '#B0B0B0',
        'hover_bg': 'rgba(255, 255, 255, 0.9)'
    }
}

# Chart settings
CHART_CONFIG = {
    'scrollZoom': True,
    'displayModeBar': True,
    'displaylogo': False,
    'modeBarButtonsToRemove': ['select2d', 'lasso2d', 'autoScale2d'],
    'doubleClick': 'reset+autosize',
    'showTips': True,
    'responsive': True
}

"""Application settings."""

import os

# Database settings
DB_SETTINGS = {
    'db_path': os.path.join(os.path.dirname(__file__), '..', 'data', 'market_data.db'),
    'echo': False  # Set to True for SQL query logging
}

# Data provider settings
DATA_SETTINGS = {
    'default_provider': 'yahoo',  # 'yahoo' or 'alphavantage'
    'default_interval': '1d',
    'cache_timeout': 15,  # minutes
    'api_keys': {
        'alphavantage': os.getenv('ALPHA_VANTAGE_API_KEY')
    }
}

# Chart settings
CHART_SETTINGS = {
    'theme': 'plotly_dark',
    'height': 600,
    'margin': {'l': 40, 'r': 40, 't': 40, 'b': 40}
}
