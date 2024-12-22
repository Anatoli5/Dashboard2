from typing import List, Dict, Optional
import requests
import streamlit as st
from core.settings_manager import SettingsManager
import time

class SymbolSearchResult:
    def __init__(self, symbol: str, name: str, type: str, currency: str, match_score: float):
        self.symbol = symbol
        self.name = name
        self.type = type
        self.currency = currency
        self.match_score = match_score

    @staticmethod
    def from_alpha_vantage(data: Dict) -> 'SymbolSearchResult':
        return SymbolSearchResult(
            symbol=data.get('1. symbol', ''),
            name=data.get('2. name', ''),
            type=data.get('3. type', ''),
            currency=data.get('8. currency', 'USD'),
            match_score=float(data.get('9. matchScore', 0.0))
        )

class SymbolSearch:
    """Provider-specific symbol search functionality"""

    @staticmethod
    def search_alpha_vantage(keywords: str, min_score: float = 0.5) -> List[SymbolSearchResult]:
        """Search for symbols using Alpha Vantage API"""
        api_key = SettingsManager.get_setting('alpha_vantage_key')
        if not api_key:
            st.error("Alpha Vantage API key is required for symbol search")
            return []

        url = 'https://www.alphavantage.co/query'
        params = {
            'function': 'SYMBOL_SEARCH',
            'keywords': keywords,
            'apikey': api_key
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if 'bestMatches' not in data:
                st.warning("No matches found or API limit reached")
                return []

            results = []
            for match in data['bestMatches']:
                result = SymbolSearchResult.from_alpha_vantage(match)
                if result.match_score >= min_score:
                    results.append(result)

            return results

        except requests.exceptions.RequestException as e:
            st.error(f"Error searching symbols: {str(e)}")
            return []

    @staticmethod
    def render_symbol_search():
        """Render symbol search UI"""
        st.sidebar.subheader("🔍 Symbol Search")
        
        provider = SettingsManager.get_setting('data_provider')
        if provider != 'alpha_vantage':
            st.sidebar.info("Symbol search is available for Alpha Vantage provider")
            return

        keywords = st.sidebar.text_input(
            "Search Keywords",
            help="Enter company name, symbol, or keywords",
            key="symbol_search_input"
        )

        if keywords:
            with st.sidebar:
                with st.spinner("Searching symbols..."):
                    results = SymbolSearch.search_alpha_vantage(keywords)
                
                if results:
                    st.write("Found matches:")
                    for result in results:
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.write(f"**{result.symbol}** - {result.name}")
                            st.caption(f"Type: {result.type}, Currency: {result.currency}")
                        with col2:
                            if st.button("Add", key=f"add_{result.symbol}"):
                                from core.ticker_manager import TickerManager
                                current_tickers = TickerManager.get_selected_tickers()
                                if result.symbol not in current_tickers:
                                    TickerManager.set_selected_tickers(
                                        current_tickers + [result.symbol]
                                    )
                                    st.success(f"Added {result.symbol}")
                                else:
                                    st.info(f"{result.symbol} already added")
                else:
                    st.info("No matches found. Try different keywords.") 