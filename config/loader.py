from pathlib import Path

import pandas as pd
import streamlit as st


class ConfigLoader:
    @staticmethod
    def load_tickers(file_path: Path) -> pd.DataFrame:
        try:
            df = pd.read_csv(file_path)
            if 'ticker' in df.columns:
                return df
            df = pd.read_csv(file_path, header=None, names=["ticker", "name"])
            if 'ticker' in df.columns:
                return df
            raise ValueError(
                "Unable to find 'ticker' column in the provided CSV file."
            )
        except Exception as e:
            st.error(f"Error reading ticker CSV: {e}")
            st.stop()
