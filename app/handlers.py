"""
Command handler module.
Manages command registration and execution.
"""

from typing import Callable, Dict, List, Any
from app.context import SessionContext


class CommandHandler:
    """Handles command registration and execution."""

    def __init__(self, context=None):
        """Initialize the command handler with built-in commands."""
        self.commands: Dict[str, Callable] = {}
        self.context = context or SessionContext()
        self._register_builtin_commands()

    def _register_builtin_commands(self):
        """Register built-in commands."""
        self.register("help", self._help_command)
        self.register("exit", self._exit_command)
        self.register("quit", self._exit_command)

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
        return handler(self.context, args, kwargs)

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

def echo_command(context: SessionContext, args: List[str], kwargs: Dict[str, Any]) -> str:
    """
    Echo command for testing.

    Args:
        context: Session context
        args: Positional arguments
        kwargs: Keyword arguments

    Returns:
        Echoed string
    """
    return ' '.join(args) + ' ' + ' '.join(f"{key}={value}" for key, value in kwargs.items()) + " " + context.state.get("test")