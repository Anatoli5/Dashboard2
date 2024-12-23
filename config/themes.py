"""Color schemes for the application."""

COLOR_SCHEMES = {
    'dark': {
        # Main backgrounds
        'page_bg': '#121212',
        'sidebar_bg': '#1E1E1E',
        'chart_outer_bg': '#1a1a1a',
        'chart_inner_bg': '#222222',
        
        # Text colors
        'text_primary': '#FFFFFF',
        'text_secondary': '#B3B3B3',
        
        # UI elements
        'border': '#333333',
        'grid': '#333333',
        'hover_bg': '#111111',
        
        # Chart colors
        'chart_colors': [
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
    },
    'light': {
        # Main backgrounds
        'page_bg': '#FFFFFF',
        'sidebar_bg': '#F8F9FA',
        'chart_outer_bg': '#F0F0F0',
        'chart_inner_bg': '#FFFFFF',
        
        # Text colors
        'text_primary': '#000000',
        'text_secondary': '#6C757D',
        
        # UI elements
        'border': '#DEE2E6',
        'grid': '#E9ECEF',
        'hover_bg': '#FFFFFF',
        
        # Chart colors - same as dark theme for consistency
        'chart_colors': [
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