"""
Command handler module.
Manages command registration and execution.
"""

from typing import Callable, Dict, List, Any
from app.context import SessionContext

from app.evaluator import Evaluator


class CommandHandler:
    """Handles command registration and execution."""

    def __init__(self, context=None, evaluator: Evaluator=None):
        """Initialize the command handler with built-in commands."""
        self.commands: Dict[str, Callable] = {}
        self.context = context or SessionContext()
        self.evaluator = evaluator
        self._register_builtin_commands()

    def _register_builtin_commands(self):
        """Register built-in commands."""
        self.register("help", self._help_command)
        self.register("exit", self._exit_command)
        self.register("quit", self._exit_command)
        self.register("e", self._edit_command)
        self.register("p", self._print_command)
        self.register("v", self._evaluate_command)

    def register(self, command_name: str, handler: Callable):
        """
        Register a command handler.

        Args:
            command_name: Name of the command
            handler: Function to handle the command
        """
        self.commands[command_name.lower()] = handler

    def execute(self, command: str, args: List[str], kwargs: Dict[str, Any]) -> Any:
        """
        Execute a command.

        Args:
            command: Command name
            args: Positional arguments
            kwargs: Keyword arguments

        Returns:
            Result from command handler
        """
        if not command:
            return None

        if command not in self.commands:
            return f"Unknown command: {command}. Type 'help' for available commands."

        handler = self.commands[command]

        try:
            a = handler(args, kwargs)
            return a

        except Exception as e:
            self.context.logger.error(f"Error executing command '{command}': {e}")
            return f"{e}"

    def _help_command(self, context: SessionContext, args: List[str], kwargs: Dict[str, Any]) -> str:
        """
        Display help information.

        Args:
            args: Positional arguments (unused)
            kwargs: Keyword arguments (unused)

        Returns:
            Help message
        """
        help_text = "Available commands:\n"
        for cmd in sorted(self.commands.keys()):
            help_text += f"  - {cmd}\n"
        help_text += "\nType '<command> --help' for command-specific help."
        return help_text

    def _exit_command(self, context: SessionContext, args: List[str], kwargs: Dict[str, Any]) -> None:
        """
        Exit the REPL.

        Args:
            args: Positional arguments (unused)
            kwargs: Keyword arguments (unused)
        """
        raise EOFError()

    def _edit_command(self, args, kwargs):
        """
        Edit a spreadsheet cell

        Args:
            args: Positional arguments (e.g., command ID)
            kwargs: Keyword arguments (e.g., new command text)
        """

        if len(args) < 2:
            raise ValueError("Usage: edit <cell> <new_value>")

        cell = args[0]
        new_value = args[1]

        # Verify cell format
        if not cell[0].isalpha() or not cell[1:].isdigit():
            raise ValueError("Invalid cell reference. Use format like A1, B2, etc.")

        # Update the spreadsheet state
        self.context.state.spreadsheet[cell] = self.evaluator.string_to_expression(cell, new_value)
        self.context.logger.info(f"Updated cell {cell} to '{new_value}'")

        # Update upstream dependencies and mark dependents as dirty
        self.evaluator.mark_dependencies(cell)
        self.evaluator.update_dependencies(cell)
        self.context.state.dirty_cells.add(cell)

        return f"Cell {cell} updated to '{new_value}'"

    def _print_command(self, args, kwargs):
        """
        Print a spreadsheet cell value

        Args:
            args: Positional arguments (e.g., cell reference)
            kwargs: Keyword arguments (unused)
        """

        if len(args) < 1:
            raise ValueError("Usage: print <cell>")

        cell = args[0]

        # Verify cell format
        if not cell[0].isalpha() or not cell[1:].isdigit():
            raise ValueError("Invalid cell reference. Use format like A1, B2, etc.")

        expression = self.context.state.spreadsheet.get(cell)
        if expression is None:
            return f"Cell {cell} is empty."

        return str(expression)

    def _evaluate_command(self, args, kwargs):
        """
        Evaluate a spreadsheet cell value

        Args:
            args: Positional arguments (e.g., cell reference)
            kwargs: Keyword arguments (unused)
        """

        if len(args) < 1:
            raise ValueError("Usage: evaluate <cell>")

        cell = args[0]

        # Verify cell format
        if not cell[0].isalpha() or not cell[1:].isdigit():
            raise ValueError("Invalid cell reference. Use format like A1, B2, etc.")

        if cell not in self.context.state.dirty_cells and cell in self.context.state.evaluation_cache:
            return str(self.context.state.evaluation_cache[cell])

        original_value = None

        if cell in self.context.state.evaluation_cache:
            original_value = self.context.state.evaluation_cache[cell]

        expression = self.context.state.spreadsheet.get(cell)
        if expression is None:
            return f"Cell {cell} is empty."

        result = self.evaluator.evaluate(expression)
        self.context.state.evaluation_cache[cell] = result
        self.context.state.dirty_cells.discard(cell)

        if original_value != result:
            self.evaluator.update_dependencies(cell) # mark dependents as dirty since this value may have changed

        return str(result)