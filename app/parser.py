"""
Command parser module.
Handles parsing of user input into commands and arguments.
"""

import shlex
from typing import Tuple, List, Dict


class Parser:
    """Parses user input into structured commands."""

    def __init__(self):
        """Initialize the parser."""
        pass

    def parse(self, user_input: str) -> Tuple[str, List[str], Dict[str, str]]:
        """
        Parse user input into command, positional args, and keyword args.

        Args:
            user_input: Raw input string from user

        Returns:
            Tuple of (command, args, kwargs)
            - command: The command name
            - args: List of positional arguments
            - kwargs: Dictionary of keyword arguments
        """
        # Tokenize input
        tokens = self._tokenize(user_input)

        if not tokens:
            return "", [], {}

        # First token is the command
        command = tokens[0].lower()

        # Parse remaining tokens
        args, kwargs = self._parse_arguments(tokens[1:])

        return command, args, kwargs

    def _tokenize(self, user_input: str) -> List[str]:
        """
        Tokenize input string respecting quotes.

        Args:
            user_input: Raw input string

        Returns:
            List of tokens
        """
        try:
            return shlex.split(user_input)
        except ValueError:
            # Fallback to simple split if quotes are unmatched
            return user_input.split()

    def _parse_arguments(self, tokens: List[str]) -> Tuple[List[str], Dict[str, str]]:
        """
        Parse tokens into positional and keyword arguments.

        Args:
            tokens: List of argument tokens

        Returns:
            Tuple of (args, kwargs)
        """
        args = []
        kwargs = {}

        i = 0
        while i < len(tokens):
            token = tokens[i]

            # Check if it's a flag (--key or -k)
            if token.startswith('--'):
                key = token[2:]
                # Check if next token is the value
                if i + 1 < len(tokens) and not tokens[i + 1].startswith('-'):
                    kwargs[key] = tokens[i + 1]
                    i += 2
                else:
                    kwargs[key] = True
                    i += 1
            elif token.startswith('-') and len(token) > 1:
                key = token[1:]
                if i + 1 < len(tokens) and not tokens[i + 1].startswith('-'):
                    kwargs[key] = tokens[i + 1]
                    i += 2
                else:
                    kwargs[key] = True
                    i += 1
            else:
                # Positional argument
                args.append(token)
                i += 1

        return args, kwargs
