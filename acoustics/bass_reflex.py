from dataclasses import dataclass, field

import numpy as np

from acoustics.driver import Driver
from acoustics.simulation import Simulation
from core.enclosures.bass_reflex import BassReflexEnclosure


@dataclass
class BassReflex(Simulation):
    """
    Small-signal lossless bass-reflex enclosure model.

    This version calculates:

    - Compliance ratio alpha = Vas / Vb
    - Tuning ratio h = Fb / Fs
    - Normalized fourth-order transfer-function magnitude
    - Numerical lower -3 dB frequency

    The response is normalized to 0 dB at high frequency.

    Enclosure leakage, absorption losses, port losses, voice-coil
    inductance and nonlinear effects are not yet included.
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

    f3_hz: float | None = field(
        default=None,
        init=False,
    )

    def __post_init__(self) -> None:
        self._validate_inputs()

    def _validate_inputs(self) -> None:
        """Validate the parameters required by this simulation."""
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

        if self.enclosure.volume_l <= 0:
            raise ValueError(
                "Bass-reflex enclosure volume must be "
                "greater than zero."
            )

        if self.enclosure.tuning_hz <= 0:
            raise ValueError(
                "Bass-reflex tuning frequency must be "
                "greater than zero."
            )

    def _require_calculated(self) -> None:
        """Ensure calculate() has been called."""
        if (
            self.alpha is None
            or self.tuning_ratio is None
        ):
            raise RuntimeError(
                "Simulation has not been calculated. "
                "Call calculate() first."
            )

    def calculate(self) -> None:
        """Calculate the principal bass-reflex system results."""
        self.alpha = (
            self.driver.vas
            / self.enclosure.volume_l
        )

        self.tuning_ratio = (
            self.enclosure.tuning_hz
            / self.driver.fs
        )

        self.f3_hz = self.calculate_f3()

    def calculate_transfer_function(
        self,
        frequencies_hz: np.ndarray,
    ) -> np.ndarray:
        """
        Calculate normalized transfer-function magnitude in decibels.

        Parameters
        ----------
        frequencies_hz:
            One-dimensional frequency array in hertz.

        Returns
        -------
        np.ndarray:
            Relative magnitude in decibels, normalized to 0 dB at
            high frequency.
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

        if frequencies_hz.size == 0:
            raise ValueError(
                "Frequency input cannot be empty."
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
        tuning_ratio = self.tuning_ratio

        numerator = s**4

        denominator = (
            s**4
            + (1.0 / qts) * s**3
            + (
                1.0
                + alpha
                + tuning_ratio**2
            )
            * s**2
            + (
                tuning_ratio**2
                / qts
            )
            * s
            + tuning_ratio**2
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

        return 20.0 * np.log10(
            magnitude
        )

    def calculate_f3(
        self,
        minimum_frequency_hz: float = 5.0,
        maximum_frequency_hz: float = 1000.0,
        points: int = 20_000,
    ) -> float:
        """
        Numerically find the lowest rising -3 dB crossing.

        The response is evaluated on a logarithmic frequency grid.
        Linear interpolation is then applied between the two points
        surrounding the crossing.
        """
        self._require_calculated()

        if minimum_frequency_hz <= 0:
            raise ValueError(
                "Minimum frequency must be greater than zero."
            )

        if (
            maximum_frequency_hz
            <= minimum_frequency_hz
        ):
            raise ValueError(
                "Maximum frequency must exceed minimum frequency."
            )

        if points < 2:
            raise ValueError(
                "At least two frequency points are required."
            )

        frequencies_hz = np.logspace(
            np.log10(minimum_frequency_hz),
            np.log10(maximum_frequency_hz),
            points,
        )

        magnitude_db = (
            self.calculate_transfer_function(
                frequencies_hz
            )
        )

        target_db = -3.0103

        above_target = (
            magnitude_db >= target_db
        )

        crossing_indices = np.where(
            np.diff(
                above_target.astype(int)
            )
            == 1
        )[0]

        if crossing_indices.size == 0:
            raise RuntimeError(
                "Could not find a rising -3 dB crossing "
                "within the selected frequency range."
            )

        crossing_index = int(
            crossing_indices[0]
        )

        frequency_1 = frequencies_hz[
            crossing_index
        ]

        frequency_2 = frequencies_hz[
            crossing_index + 1
        ]

        magnitude_1 = magnitude_db[
            crossing_index
        ]

        magnitude_2 = magnitude_db[
            crossing_index + 1
        ]

        magnitude_difference = (
            magnitude_2 - magnitude_1
        )

        if magnitude_difference == 0:
            return float(frequency_1)

        interpolation_fraction = (
            target_db - magnitude_1
        ) / magnitude_difference

        f3_hz = (
            frequency_1
            + interpolation_fraction
            * (
                frequency_2
                - frequency_1
            )
        )

        return float(f3_hz)

    def summary(self) -> None:
        """Print a concise bass-reflex simulation summary."""
        self._require_calculated()

        print("=" * 50)
        print("Bass-reflex simulation")
        print("=" * 50)

        print(
            "Driver       : "
            f"{self.driver.manufacturer} "
            f"{self.driver.model}"
        )

        print(
            "Box volume   : "
            f"{self.enclosure.volume_l:.2f} L"
        )

        print(
            "Tuning       : "
            f"{self.enclosure.tuning_hz:.2f} Hz"
        )

        print(
            "Alpha        : "
            f"{self.alpha:.3f}"
        )

        print(
            "Tuning ratio : "
            f"{self.tuning_ratio:.3f}"
        )

        if self.f3_hz is None:
            print("F3           : N/A")
        else:
            print(
                "F3           : "
                f"{self.f3_hz:.2f} Hz"
            )