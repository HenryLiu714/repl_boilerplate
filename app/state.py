
from typing import Any, Dict
from app.models.expression import Expression


class State:
    """A simple class to hold the state of the REPL session."""

    def __init__(self):
        self.spreadsheet: Dict[str, Expression] = {} # Map of cell references to their values
        self.dependencies: Dict[str, set[str]] = {} # For cycle detection and update propagation

        self.upward_dependencies: Dict[str, set[str]] = {} # For update propogation
        self.dirty_cells: set[str] = set() # Cells that need to be re-evaluated
        self.evaluation_cache: Dict[str, Any] = {} # Cache of evaluated cell values

    def set(self, key: str, value: Any):
        """Set a value in the state."""
        self.__dict__[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from the state."""
        return self.__dict__.get(key, default)