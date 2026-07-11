from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Enclosure(ABC):
    """Base class for all enclosure definitions."""

    @property
    @abstractmethod
    def enclosure_type(self) -> str:
        """Return the enclosure type identifier."""
        raise NotImplementedError

    @abstractmethod
    def to_dict(self) -> dict:
        """Convert the enclosure into JSON-compatible data."""
        raise NotImplementedError