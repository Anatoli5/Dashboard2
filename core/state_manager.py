import json
from datetime import datetime
from pathlib import Path
import streamlit as st


class StateManager:
    STATE_FILE = "app_state.json"

    @staticmethod
    def save_state():
        """Save current application state to a file"""
        state = {
            'selected_tickers': st.session_state.get('selected_tickers', []),
            'start_date': st.session_state.get('start_date', '').isoformat() if st.session_state.get(
                'start_date') else None,
            'end_date': st.session_state.get('end_date', '').isoformat() if st.session_state.get('end_date') else None,
            'interval': st.session_state.get('interval', '1d'),
            'log_scale': st.session_state.get('log_scale', False),
            'norm_date': st.session_state.get('norm_date', '').isoformat() if st.session_state.get(
                'norm_date') else None,
            'last_shutdown': datetime.utcnow().isoformat()
        }

        try:
            with open(StateManager.STATE_FILE, 'w') as f:
                json.dump(state, f)
        except Exception as e:
            st.warning(f"Could not save application state: {str(e)}")

    @staticmethod
    def load_state():
        """Load last saved application state"""
        if not Path(StateManager.STATE_FILE).exists():
            return False

        try:
            with open(StateManager.STATE_FILE, 'r') as f:
                state = json.load(f)

            # Restore state to session
            st.session_state['selected_tickers'] = state.get('selected_tickers', [])

            # Convert ISO format strings back to datetime
            if state.get('start_date'):
                st.session_state['start_date'] = datetime.fromisoformat(state['start_date']).date()
            if state.get('end_date'):
                st.session_state['end_date'] = datetime.fromisoformat(state['end_date']).date()
            if state.get('norm_date'):
                st.session_state['norm_date'] = datetime.fromisoformat(state['norm_date'])
            else:
                st.session_state['norm_date'] = None

            st.session_state['interval'] = state.get('interval', '1d')
            st.session_state['log_scale'] = state.get('log_scale', False)

            return True
        except Exception as e:
            st.warning(f"Could not load saved state: {str(e)}")
            return False
