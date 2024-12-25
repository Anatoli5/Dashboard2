"""Color schemes for the application."""

COLOR_SCHEMES = {
    'dark': {
        # Base colors
        'bs-body-bg': '#000000',  # Darkest - base background
        'bs-body-color': '#FFFFFF',
        'bs-dark': 'rgba(255, 255, 255, 0.1)',  # Light overlay for containers
        'bs-gray-700': 'rgba(255, 255, 255, 0.15)',  # Lighter overlay for hover
        'bs-primary': '#0D6EFD',
        
        # UI Elements with transparency
        'border-color': 'rgba(255, 255, 255, 0.15)',
        'dropdown-bg': 'rgba(255, 255, 255, 0.05)',  # Subtle overlay for dropdowns
        'hover-bg': 'rgba(255, 255, 255, 0.07)',  # Slightly visible on hover
        
        # Chart overlays
        'chart-outer-bg': 'rgba(255, 255, 255, 0.08)',  # Subtle container
        'chart-inner-bg': 'rgba(255, 255, 255, 0.05)',  # More subtle for content
        'chart-grid': 'rgba(255, 255, 255, 0.1)',  # Subtle grid lines
        
        # Chart series colors (keeping solid for visibility)
        'chart-colors': [
            '#2E91E5',  # Blue
            '#E15F99',  # Pink
            '#1CA71C',  # Green
            '#FB0D0D',  # Red
            '#DA16FF',  # Purple
            '#B68100',  # Brown
            '#EB663B',  # Orange
            '#511CFB',  # Indigo
            '#00CED1',  # Dark Turquoise
            '#FFD700',  # Gold
        ]
    }
}

# Default theme to fall back on if selected theme is not available
DEFAULT_THEME = 'dark' 