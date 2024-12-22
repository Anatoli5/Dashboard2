import json
from datetime import datetime
from pathlib import Path
import streamlit as st


class StateManager:
    STATE_FILE = "app_state.json"

    @staticmethod
    def save_state(state_data: dict = None):
        """Save current application state to a file"""
        try:
            # If no state data provided, use session state
            if state_data is None:
                state_data = {
                    'selected_tickers': st.session_state.get('selected_tickers', []),
                    'start_date': st.session_state.get('start_date', '').isoformat() if st.session_state.get('start_date') else None,
                    'end_date': st.session_state.get('end_date', '').isoformat() if st.session_state.get('end_date') else None,
                    'interval': st.session_state.get('interval', '1d'),
                    'log_scale': st.session_state.get('log_scale', False),
                    'norm_date': st.session_state.get('norm_date', '').isoformat() if st.session_state.get('norm_date') else None,
                    'last_shutdown': datetime.utcnow().isoformat()
                }
            else:
                # Ensure dates are properly formatted
                if 'start_date' in state_data and state_data['start_date']:
                    state_data['start_date'] = state_data['start_date'].isoformat() if hasattr(state_data['start_date'], 'isoformat') else state_data['start_date']
                if 'end_date' in state_data and state_data['end_date']:
                    state_data['end_date'] = state_data['end_date'].isoformat() if hasattr(state_data['end_date'], 'isoformat') else state_data['end_date']
                if 'norm_date' in state_data and state_data['norm_date']:
                    state_data['norm_date'] = state_data['norm_date'].isoformat() if hasattr(state_data['norm_date'], 'isoformat') else state_data['norm_date']
                state_data['last_shutdown'] = datetime.utcnow().isoformat()

            with open(StateManager.STATE_FILE, 'w') as f:
                json.dump(state_data, f)
            return True
        except Exception as e:
            st.warning(f"Could not save application state: {str(e)}")
            return False

    @staticmethod
    def load_state() -> dict:
        """Load last saved application state"""
        if not Path(StateManager.STATE_FILE).exists():
            return {}

        try:
            with open(StateManager.STATE_FILE, 'r') as f:
                state = json.load(f)

            # Convert ISO format strings back to datetime
            if state.get('start_date'):
                state['start_date'] = datetime.fromisoformat(state['start_date']).date()
            if state.get('end_date'):
                state['end_date'] = datetime.fromisoformat(state['end_date']).date()
            if state.get('norm_date'):
                state['norm_date'] = datetime.fromisoformat(state['norm_date'])

            return state
        except Exception as e:
            st.warning(f"Could not load saved state: {str(e)}")
            return {}
