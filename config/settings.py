from pathlib import Path


class Settings:
    DB_PATH: str = "data.db"
    TICKERS_FILE: Path = Path("files/crypto_tickers.csv")
    DEFAULT_INTERVAL: str = "1d"
    DEFAULT_PERIOD: str = "max"

    @staticmethod
    def get_db_url() -> str:
        return f"sqlite:///{Settings.DB_PATH}"
