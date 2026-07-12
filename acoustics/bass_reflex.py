from dataclasses import dataclass, field

import numpy as np

from acoustics.driver import Driver
from acoustics.simulation import Simulation
from core.enclosures.bass_reflex import BassReflexEnclosure


@dataclass
class BassReflex(Simulation):
    """
    Small-signal lossless bass-reflex enclosure model.

    The current implementation calculates the normalized fourth-order
    transfer-function magnitude. Losses are not yet included.
    """

    driver: Driver
    enclosure: BassReflexEnclosure

    alpha: float | None = field(
        default=None,
        init=False,
    )

    tuning_ratio: float | None = field(
        default=None,
        init=False,
    )

    def __post_init__(self) -> None:
        self._validate_inputs()

    def _validate_inputs(self) -> None:
        if self.driver.fs is None:
            raise ValueError(
                "Cannot simulate bass reflex: Fs is missing."
            )

        if self.driver.qts is None:
            raise ValueError(
                "Cannot simulate bass reflex: Qts is missing."
            )

        if self.driver.vas is None:
            raise ValueError(
                "Cannot simulate bass reflex: Vas is missing."
            )

        if self.driver.fs <= 0:
            raise ValueError(
                "Driver Fs must be greater than zero."
            )

        if self.driver.qts <= 0:
            raise ValueError(
                "Driver Qts must be greater than zero."
            )

        if self.driver.vas <= 0:
            raise ValueError(
                "Driver Vas must be greater than zero."
            )

    def _require_calculated(self) -> None:
        if (
            self.alpha is None
            or self.tuning_ratio is None
        ):
            raise RuntimeError(
                "Simulation has not been calculated. "
                "Call calculate() first."
            )

    def calculate(self) -> None:
        """Calculate normalized bass-reflex system parameters."""
        self.alpha = (
            self.driver.vas
            / self.enclosure.volume_l
        )

        self.tuning_ratio = (
            self.enclosure.tuning_hz
            / self.driver.fs
        )

    def calculate_transfer_function(
        self,
        frequencies_hz: np.ndarray,
    ) -> np.ndarray:
        """
        Calculate normalized bass-reflex magnitude in decibels.

        The response is normalized to 0 dB at high frequency.
        """
        self._require_calculated()

        frequencies_hz = np.asarray(
            frequencies_hz,
            dtype=float,
        )

        if frequencies_hz.ndim != 1:
            raise ValueError(
                "Frequency input must be one-dimensional."
            )

        if np.any(frequencies_hz <= 0):
            raise ValueError(
                "All frequencies must be greater than zero."
            )

        normalized_frequency = (
            frequencies_hz
            / self.driver.fs
        )

        s = 1j * normalized_frequency

        qts = self.driver.qts
        alpha = self.alpha
        h = self.tuning_ratio

        numerator = s**4

        denominator = (
            s**4
            + (1.0 / qts) * s**3
            + (1.0 + alpha + h**2) * s**2
            + (h**2 / qts) * s
            + h**2
        )

        transfer_function = (
            numerator / denominator
        )

        magnitude = np.abs(
            transfer_function
        )

        magnitude = np.maximum(
            magnitude,
            np.finfo(float).tiny,
        )

        return 20.0 * np.log10(magnitude)

    def summary(self) -> None:
        """Print a concise simulation summary."""
        self._require_calculated()

        print("=" * 50)
        print("Bass-reflex simulation")
        print("=" * 50)

        print(
            f"Driver       : "
            f"{self.driver.manufacturer} "
            f"{self.driver.model}"
        )

        print(
            f"Box volume   : "
            f"{self.enclosure.volume_l:.2f} L"
        )

        print(
            f"Tuning       : "
            f"{self.enclosure.tuning_hz:.2f} Hz"
        )

        print(
            f"Alpha        : "
            f"{self.alpha:.3f}"
        )

        print(
            f"Tuning ratio : "
            f"{self.tuning_ratio:.3f}"
        )