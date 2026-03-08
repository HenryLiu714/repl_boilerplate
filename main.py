#!/usr/bin/env python3
"""
Main entry point for the REPL application.
"""

from app.config import Config
from app.parser import Parser
from app.handlers import CommandHandler
from app.context import SessionContext
from app.repository import InMemoryRepository
from app.utils import setup_logging, format_response

import logging


def main():
    """Main REPL loop."""
    # Initialize components
    config = Config()
    parser = Parser()
    logger = setup_logging(config.log_level)

    if config.log_file:
        file_handler = logging.FileHandler(config.log_file)
        file_handler.setLevel(getattr(logging, config.log_level.upper()))
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    repository = InMemoryRepository()  # Initialize your repository here

    context = SessionContext(logger=logger, repository=repository, config=config)  # Add repository if needed
    handler = CommandHandler(context=context)

    logger.info("Starting REPL...")
    print(config.welcome_message)

    while True:
        try:
            # Read input
            user_input = input(config.prompt).strip()

            # Skip empty input
            if not user_input:
                continue

            # Parse command
            command, args, kwargs = parser.parse(user_input)

            # Execute command
            result = handler.execute(command, args, kwargs)

            # Display result
            if result is not None:
                print(format_response(result))

        except KeyboardInterrupt:
            print("\n" + config.exit_message)
            break
        except EOFError:
            print("\n" + config.exit_message)
            break
        except Exception as e:
            logger.error(f"Error: {e}")
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
