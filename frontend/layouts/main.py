"""Main application layout."""

from dash import html
import dash_bootstrap_components as dbc
from config.settings import THEME

def create_layout():
    """Create the main application layout."""
    return dbc.Container([
        # Store components for state management
        dbc.Row([
            # Sidebar
            dbc.Col([
                html.Div(id='sidebar-container', className='sidebar')
            ], width=3),
            
            # Main content
            dbc.Col([
                # Chart area
                html.Div(id='chart-container', className='chart-container'),
                
                # Info area below chart
                html.Div(id='info-container', className='info-container')
            ], width=9)
        ])
    ], fluid=True, className='app-container') 