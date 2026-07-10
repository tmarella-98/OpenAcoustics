from abc import ABC, abstractmethod


class Simulation(ABC):
    """Base class for all OpenAcoustics simulations."""

    @abstractmethod
    def calculate(self) -> None:
        """Run the simulation calculations."""
        raise NotImplementedError

    @abstractmethod
    def summary(self) -> None:
        """Display a concise summary of the results."""
        raise NotImplementedError