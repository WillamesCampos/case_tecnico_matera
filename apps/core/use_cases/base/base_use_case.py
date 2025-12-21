from abc import ABC, abstractmethod

from credit_track.settings import logger


class BaseUseCase(ABC):
    """Base class for all use cases."""

    def __init__(self):
        self.logger = logger

    @abstractmethod
    def execute(self, *args, **kwargs):
        """
        Execute the use case.

        This method must be implemented by all subclasses.

        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError("Subclasses must implement this method")
