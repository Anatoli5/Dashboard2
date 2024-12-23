"""State management for the application."""

import json
from pathlib import Path
from typing import Dict, Any, Optional

class StateManager:
    """Manages application state persistence."""
    
    STATE_FILE = Path("app_state.json")
    _state = None
    
    @classmethod
    def load_state(cls) -> Dict:
        """Load state from file."""
        if cls._state is None:
            try:
                if cls.STATE_FILE.exists():
                    with open(cls.STATE_FILE, 'r') as f:
                        cls._state = json.load(f)
                else:
                    cls._state = {}
            except Exception as e:
                print(f"Error loading state: {str(e)}")
                cls._state = {}
        return cls._state
    
    @classmethod
    def save_state(cls, state: Dict) -> None:
        """Save state to file."""
        try:
            cls._state = state
            with open(cls.STATE_FILE, 'w') as f:
                json.dump(state, f, indent=4)
        except Exception as e:
            print(f"Error saving state: {str(e)}")
    
    @classmethod
    def get_state(cls, key: str, default: Any = None) -> Any:
        """Get a value from state."""
        state = cls.load_state()
        return state.get(key, default)
    
    @classmethod
    def set_state(cls, key: str, value: Any) -> None:
        """Set a value in state."""
        state = cls.load_state()
        state[key] = value
        cls.save_state(state)
    
    @classmethod
    def update_state(cls, updates: Dict[str, Any]) -> None:
        """Update multiple state values."""
        state = cls.load_state()
        state.update(updates)
        cls.save_state(state)
