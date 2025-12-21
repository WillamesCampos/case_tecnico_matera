from credit_track.settings import logger


class BaseService:
    """Base class for all services."""

    def __init__(self):
        self.logger = logger
