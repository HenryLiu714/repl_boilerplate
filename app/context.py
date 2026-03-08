import logging

class SessionContext:
    """Holds the state and configuration for a REPL session."""

    def __init__(self, repository=None, logger=None, config=None):
        self.state = {}
        self.repository = repository
        self.logger = logger or logging.getLogger(__name__)
        self.config = config