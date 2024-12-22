from typing import Dict, Any, Optional
import streamlit as st
from datetime import datetime, timedelta
import json
import os

class SettingsManager:
    """Manages application settings"""
    
    _settings_file = "settings.json"
    _settings = None
    _initialized = False
    
    @classmethod
    def initialize_settings(cls) -> None:
        """Initialize settings from file or defaults"""
        if cls._initialized:
            return
            
        try:
            if os.path.exists(cls._settings_file):
                with open(cls._settings_file, 'r') as f:
                    cls._settings = json.load(f)
            else:
                cls._settings = {}
                
            # Set defaults if not present
            defaults = {
                'theme': 'dark',
                'data_provider': 'yahoo',
                'alpha_vantage_key': '',
                'chart_height': 600
            }
            
            for key, value in defaults.items():
                if key not in cls._settings:
                    cls._settings[key] = value
                    
            cls._initialized = True
            
        except Exception as e:
            print(f"Error initializing settings: {str(e)}")
            cls._settings = {}
    
    @classmethod
    def save_settings(cls) -> None:
        """Save settings to file"""
        if not cls._settings:
            return
            
        try:
            with open(cls._settings_file, 'w') as f:
                json.dump(cls._settings, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {str(e)}")
    
    @classmethod
    def get_setting(cls, key: str, default: Any = None) -> Any:
        """Get a setting value"""
        if not cls._settings:
            cls.initialize_settings()
        return cls._settings.get(key, default)
    
    @classmethod
    def set_setting(cls, key: str, value: Any) -> None:
        """Set a setting value"""
        if not cls._settings:
            cls.initialize_settings()
            
        if cls._settings.get(key) != value:
            cls._settings[key] = value
            # Only trigger rerun if we're in a Streamlit context
            if hasattr(st, 'session_state'):
                st.session_state.needs_rerun = True
    
    @classmethod
    def get_all_settings(cls) -> Dict[str, Any]:
        """Get all settings"""
        if not cls._settings:
            cls.initialize_settings()
        return cls._settings.copy()

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
                            SettingsManager.set_setting('alpha_vantage_key', api_key)
                            provider_changed = True
                            st.success("API key saved!")
                        else:
                            st.error("API key required")
                
                if not api_key and current_provider == 'alpha_vantage':
                    st.warning("API key required for Alpha Vantage")
                    SettingsManager.set_setting('alpha_vantage_key', '')
                    provider_changed = True
            
            elif new_provider != current_provider:
                SettingsManager.set_setting('alpha_vantage_key', '')
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
                SettingsManager.set_setting('max_retries', max_retries)
                SettingsManager.set_setting('retry_delay', retry_delay)
        
        return provider_changed