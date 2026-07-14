from dataclasses import dataclass

import numpy as np

from acoustics.driver import Driver
from core.enclosures.sealed import SealedEnclosure


@dataclass
class ExcursionCalculator:
    """Calculate cone excursion for loudspeaker systems."""

    driver: Driver
    enclosure: SealedEnclosure

    def calculate(
        self,
        frequencies_hz: np.ndarray,
        input_power_w: float,
    ) -> np.ndarray:
        """
        Return cone excursion in millimetres.

        Not implemented yet.
        """
        raise NotImplementedError