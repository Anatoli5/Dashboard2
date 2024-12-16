# helpers.py
from typing import Union

def format_currency(value: Union[float, int]) -> str:
    return f"${value:,.2f}"
