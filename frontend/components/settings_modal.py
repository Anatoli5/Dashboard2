"""Settings modal component."""

from dash import html, dcc
import dash_bootstrap_components as dbc

# Theme URLs
THEME_URLS = {
    'DARKLY': "https://cdn.jsdelivr.net/npm/bootswatch@5.3.3/dist/darkly/bootstrap.min.css",
    'CYBORG': "https://cdn.jsdelivr.net/npm/bootswatch@5.3.3/dist/cyborg/bootstrap.min.css",
    'SLATE': "https://cdn.jsdelivr.net/npm/bootswatch@5.3.3/dist/slate/bootstrap.min.css",
    'FLATLY': "https://cdn.jsdelivr.net/npm/bootswatch@5.3.3/dist/flatly/bootstrap.min.css"
}

# Available themes
THEMES = [
    {'label': 'Darkly (Dark)', 'value': THEME_URLS['DARKLY']},
    {'label': 'Cyborg (Dark)', 'value': THEME_URLS['CYBORG']},
    {'label': 'Slate (Dark)', 'value': THEME_URLS['SLATE']},
    {'label': 'Flatly (Light)', 'value': THEME_URLS['FLATLY']},
]

def create_color_swatch(name, var_name):
    """Create a color swatch with label."""
    return html.Div([
        html.Div(style={
            "backgroundColor": f"var(--bs-{var_name})",
            "height": "30px",
            "width": "100%",
            "borderRadius": "4px",
            "marginBottom": "4px",
            "border": "1px solid var(--bs-gray-700)"
        }),
        html.Div(f"{name} (--bs-{var_name})", 
                style={"fontSize": "12px", "opacity": "0.8"})
    ], className="mb-3")

def create_settings_modal():
    """Create the settings modal."""
    return dbc.Modal([
        dbc.ModalHeader([
            dbc.ModalTitle("Settings"),
            dbc.Button(
                "×",
                id="settings-close",
                className="ms-auto",
                n_clicks=0,
                style={
                    "fontSize": "24px",
                    "padding": "0 6px",
                    "marginBottom": "3px"
                }
            )
        ], className="border-0"),
        dbc.ModalBody([
            # Theme selector
            html.Div([
                html.Label("Theme", className="mb-2"),
                dcc.Dropdown(
                    id='theme-selector',
                    options=THEMES,
                    value=THEME_URLS['DARKLY'],  # Default theme
                    clearable=False,
                    className="mb-3 dash-dropdown-dark"
                ),
            ], className="mb-4"),
            
            # Color palette
            html.Div([
                html.H6("Color Palette", className="mb-3"),
                html.Div([
                    create_color_swatch("Primary", "primary"),
                    create_color_swatch("Secondary", "secondary"),
                    create_color_swatch("Success", "success"),
                    create_color_swatch("Info", "info"),
                    create_color_swatch("Warning", "warning"),
                    create_color_swatch("Danger", "danger"),
                    html.Hr(style={"margin": "1rem 0"}),
                    create_color_swatch("Background", "body-bg"),
                    create_color_swatch("Text", "body-color"),
                    create_color_swatch("Link", "link-color"),
                    html.Hr(style={"margin": "1rem 0"}),
                    create_color_swatch("Dark", "dark"),
                    create_color_swatch("Light", "light"),
                ], id="color-palette")
            ], className="mb-4"),
            
            # Usage examples
            html.Div([
                html.H6("Common Elements", className="mb-3"),
                dbc.Button("Primary Button", color="primary", className="me-2 mb-2"),
                dbc.Button("Secondary Button", color="secondary", className="me-2 mb-2"),
                dbc.Button("Success Button", color="success", className="me-2 mb-2"),
                html.Br(),
                dbc.Badge("Primary Badge", color="primary", className="me-2"),
                dbc.Badge("Info Badge", color="info", className="me-2"),
                dbc.Badge("Warning Badge", color="warning", className="me-2"),
            ], className="mb-4")
        ], className="px-4"),
    ], id="settings-modal", is_open=False, size="lg", backdrop="static") 