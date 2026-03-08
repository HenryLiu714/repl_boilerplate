"""
Utility functions for the REPL application.
"""

import logging
from typing import Any


def setup_logging(level: str = "INFO") -> logging.Logger:
    """
    Set up logging configuration.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Configured logger instance
    """
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    return logging.getLogger(__name__)


def format_response(response: Any) -> str:
    """
    Format a response for display.

    Args:
        response: Response data to format

    Returns:
        Formatted string
    """
    if isinstance(response, str):
        return response
    elif isinstance(response, (list, tuple)):
        return '\n'.join(str(item) for item in response)
    elif isinstance(response, dict):
        return '\n'.join(f"{key}: {value}" for key, value in response.items())
    else:
        return str(response)


def sanitize_input(user_input: str) -> str:
    """
    Sanitize user input for security.

    Args:
        user_input: Raw input from user

    Returns:
        Sanitized input
    """
    # Basic sanitization - extend as needed
    return user_input.strip()


def validate_args(args: list, min_args: int = 0, max_args: int = None) -> bool:
    """
    Validate argument count.

    Args:
        args: List of arguments
        min_args: Minimum required arguments
        max_args: Maximum allowed arguments (None for unlimited)

    Returns:
        True if valid, False otherwise
    """
    if len(args) < min_args:
        return False
    if max_args is not None and len(args) > max_args:
        return False
    return True
