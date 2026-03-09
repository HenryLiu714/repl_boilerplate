"""
Configuration module for the REPL application.
"""


class Config:
    """Configuration settings for the REPL."""

    def __init__(self):
        """Initialize configuration with default values."""
        # REPL appearance
        self.prompt = ">>> "
        self.welcome_message = "Welcome to the REPL! Type 'help' for available commands."
        self.exit_message = "Goodbye!"

        # Logging
        self.log_level = "ERROR"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
        self.log_file = "logs/repl.log"