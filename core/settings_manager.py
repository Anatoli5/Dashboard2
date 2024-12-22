from typing import Dict, Any, Optional
import streamlit as st
from datetime import datetime, timedelta
import json
from pathlib import Path
import atexit

class Settings:
    """Settings configuration class"""
    
    SETTINGS_FILE = "app_settings.json"
    
    # Default settings
    DEFAULTS = {
        'data_provider': 'yahoo',
        'alpha_vantage_key': None,
        'interval': '1d',
        'log_scale': False,
        'theme': 'dark',
        'cache_timeout': 3600,  # 1 hour in seconds
        'max_retries': 3,
        'retry_delay': 2
    }

class SettingsManager:
    """Manages application settings and their persistence"""
    
    @staticmethod
    def load_settings():
        """Load settings from file"""
        if Path(Settings.SETTINGS_FILE).exists():
            try:
                with open(Settings.SETTINGS_FILE, 'r') as f:
                    settings = json.load(f)
                    # Ensure all default settings exist
                    for key, value in Settings.DEFAULTS.items():
                        if key not in settings:
                            settings[key] = value
                    return settings
            except Exception:
                return Settings.DEFAULTS.copy()
        return Settings.DEFAULTS.copy()
    
    @staticmethod
    def save_settings():
        """Save settings to file"""
        if hasattr(st, 'session_state') and 'settings' in st.session_state:
            try:
                with open(Settings.SETTINGS_FILE, 'w') as f:
                    json.dump(st.session_state.settings, f)
            except Exception as e:
                st.warning(f"Could not save settings: {str(e)}")
    
    @staticmethod
    def initialize_settings():
        """Initialize settings in session state"""
        if 'settings' not in st.session_state:
            st.session_state.settings = SettingsManager.load_settings()
            # Register cleanup handler
            atexit.register(SettingsManager.save_settings)
    
    @staticmethod
    def get_setting(key: str, default: Any = None) -> Any:
        """Get a setting value"""
        SettingsManager.initialize_settings()
        return st.session_state.settings.get(key, default)
    
    @staticmethod
    def set_setting(key: str, value: Any):
        """Set a setting value"""
        SettingsManager.initialize_settings()
        if st.session_state.settings.get(key) != value:
            st.session_state.settings[key] = value
            SettingsManager.save_settings()
        
    @staticmethod
    def update_settings(settings: Dict[str, Any]):
        """Update multiple settings at once"""
        SettingsManager.initialize_settings()
        changed = False
        for key, value in settings.items():
            if st.session_state.settings.get(key) != value:
                st.session_state.settings[key] = value
                changed = True
        if changed:
            SettingsManager.save_settings()

class SettingsUI:
    """UI component for settings management"""
    
    @staticmethod
    def render_settings_section():
        """Render the settings section in the sidebar"""
        st.sidebar.subheader("⚙️ Settings")
        
        # Create tabs for different settings categories
        settings_tab, advanced_tab = st.sidebar.tabs(["General", "Advanced"])
        
        provider_changed = False
        
        with settings_tab:
            # Data Provider Settings
            st.subheader("Data Provider")
            current_provider = SettingsManager.get_setting('data_provider')
            
            provider = st.selectbox(
                "Select Provider",
                ["Yahoo Finance", "Alpha Vantage"],
                index=0 if current_provider == 'yahoo' else 1,
                key='settings_provider_select'
            )
            
            new_provider = 'yahoo' if provider == "Yahoo Finance" else 'alpha_vantage'
            
            # Handle Alpha Vantage API key
            if new_provider == 'alpha_vantage':
                saved_key = SettingsManager.get_setting('alpha_vantage_key')
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    api_key = st.text_input(
                        "API Key",
                        value=saved_key if saved_key else "",
                        type="password",
                        help="Get your key at alphavantage.co",
                        key="alpha_vantage_key_input"
                    )
                
                with col2:
                    if st.button("Apply", key="apply_api_key"):
                        if api_key:
                            SettingsManager.update_settings({
                                'data_provider': 'alpha_vantage',
                                'alpha_vantage_key': api_key
                            })
                            provider_changed = True
                            st.success("API key saved!")
                        else:
                            st.error("API key required")
                
                if not api_key and current_provider == 'alpha_vantage':
                    st.warning("API key required for Alpha Vantage")
                    SettingsManager.update_settings({
                        'data_provider': 'yahoo',
                        'alpha_vantage_key': None
                    })
                    provider_changed = True
            
            elif new_provider != current_provider:
                SettingsManager.update_settings({
                    'data_provider': 'yahoo',
                    'alpha_vantage_key': None
                })
                provider_changed = True
            
            # Chart Settings
            st.subheader("Chart Settings")
            theme = st.selectbox(
                "Theme",
                ["dark", "light"],
                index=0 if SettingsManager.get_setting('theme') == 'dark' else 1,
                key="theme_select"
            )
            if theme != SettingsManager.get_setting('theme'):
                SettingsManager.set_setting('theme', theme)
        
        with advanced_tab:
            # Cache Settings
            st.subheader("Cache Settings")
            cache_timeout = st.number_input(
                "Cache Timeout (seconds)",
                min_value=300,
                max_value=86400,
                value=SettingsManager.get_setting('cache_timeout'),
                step=300,
                key="cache_timeout_input"
            )
            if cache_timeout != SettingsManager.get_setting('cache_timeout'):
                SettingsManager.set_setting('cache_timeout', cache_timeout)
            
            # API Settings
            st.subheader("API Settings")
            max_retries = st.number_input(
                "Max Retries",
                min_value=1,
                max_value=5,
                value=SettingsManager.get_setting('max_retries'),
                key="max_retries_input"
            )
            retry_delay = st.number_input(
                "Retry Delay (seconds)",
                min_value=1,
                max_value=10,
                value=SettingsManager.get_setting('retry_delay'),
                key="retry_delay_input"
            )
            if max_retries != SettingsManager.get_setting('max_retries') or \
               retry_delay != SettingsManager.get_setting('retry_delay'):
                SettingsManager.update_settings({
                    'max_retries': max_retries,
                    'retry_delay': retry_delay
                })
        
        return provider_changed