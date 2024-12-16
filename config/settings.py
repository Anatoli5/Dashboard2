import yaml
from pathlib import Path

# Load configuration from config.yaml
config_file = Path(__file__).parent / 'config.yaml'

with open(config_file, 'r') as file:
    config = yaml.safe_load(file)

DATABASE_PATH: str = config.get('database_path', 'data/data.db')
TICKERS_CSV_PATH: str = config.get('tickers_csv_path', 'data/tickers.csv')
MAX_DATE_RANGE_DAYS: int = config.get('max_date_range_days', 3650)
DATA_PROVIDER: str = config.get('data_provider', 'YahooFinance')
ALPHA_VANTAGE_API_KEY: str = config.get('alpha_vantage_api_key', '')
