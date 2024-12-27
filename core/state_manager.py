"""State management for the application."""

import json
from typing import Any, Dict, Optional

class StateManager:
    """Manages application state."""
    
    _state_file = 'app_state.json'
    _default_state = {
        'selected_tickers': [],
        'interval': '1d',
        'log_scale': False,
        'normalize': False,
        'start_date': None,
        'end_date': None,
        'norm_date': None,
        'theme': 'dark'
    }
    
    @classmethod
    def get_state(cls, key: str, default: Any = None) -> Any:
        """Get a value from the state."""
        try:
            with open(cls._state_file, 'r') as f:
                state = json.load(f)
                return state.get(key, default if default is not None else cls._default_state.get(key))
        except Exception as e:
            print(f"Error loading state: {e}")
            return default if default is not None else cls._default_state.get(key)
    
    @classmethod
    def set_state(cls, key: str, value: Any) -> None:
        """Set a value in the state."""
        try:
            try:
                with open(cls._state_file, 'r') as f:
                    state = json.load(f)
            except:
                state = cls._default_state.copy()
            
            state[key] = value
            
            with open(cls._state_file, 'w') as f:
                json.dump(state, f)
        except Exception as e:
            print(f"Error saving state: {e}")
    
    @classmethod
    def get_full_state(cls) -> Dict:
        """Get the full application state."""
        try:
            with open(cls._state_file, 'r') as f:
                return json.load(f)
        except:
            return cls._default_state.copy()
            
    @classmethod
    def load_state(cls) -> Dict:
        """Load state from file (alias for get_full_state)."""
        return cls.get_full_state()
        
    @classmethod
    def update_state(cls, updates: Dict[str, Any]) -> None:
        """Update multiple state values at once."""
        try:
            try:
                with open(cls._state_file, 'r') as f:
                    state = json.load(f)
            except:
                state = cls._default_state.copy()
            
            state.update(updates)
            
            with open(cls._state_file, 'w') as f:
                json.dump(state, f)
        except Exception as e:
            print(f"Error updating state: {e}")
