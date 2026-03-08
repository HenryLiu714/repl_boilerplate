#!/usr/bin/env python3
"""
Main entry point for the REPL application.
"""

from app.config import Config
from app.parser import Parser
from app.handlers import CommandHandler
from app.utils import setup_logging, format_response


def main():
    """Main REPL loop."""
    # Initialize components
    config = Config()
    parser = Parser()
    handler = CommandHandler()
    logger = setup_logging(config.log_level)

    handler.register("echo", lambda args, kwargs: ' '.join(args))

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
