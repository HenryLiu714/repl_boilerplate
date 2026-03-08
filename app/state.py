
from typing import Any

class State:
    """A simple class to hold the state of the REPL session."""

    def __init__(self):
        self.test = "test"

    def set(self, key: str, value: Any):
        """Set a value in the state."""
        self.__dict__[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from the state."""
        return self.__dict__.get(key, default)