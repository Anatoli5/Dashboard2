"""Callback registration and initialization."""

from dash import Dash
from .chart import register_chart_callbacks
from .data import register_data_callbacks


def register_callbacks(app: Dash) -> None:
    """Register all callbacks with the app."""
    register_chart_callbacks(app)
    register_data_callbacks(app) 