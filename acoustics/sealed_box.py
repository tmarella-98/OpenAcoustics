import math
from dataclasses import dataclass, field

import matplotlib.pyplot as plt
import numpy as np

from acoustics.driver import Driver
from acoustics.simulation import Simulation
from acoustics.units import litres_to_cubic_metres


@dataclass
class SealedBox(Simulation):
    """Small-signal lumped-parameter model of a sealed enclosure."""

    driver: Driver
    volume_l: float

    fc_hz: float | None = field(default=None, init=False)
    qtc: float | None = field(default=None, init=False)
    f3_hz: float | None = field(default=None, init=False)

    def __post_init__(self) -> None:
        self._validate_inputs()

    def _validate_inputs(self) -> None:
        if self.volume_l <= 0:
            raise ValueError(
                "Sealed-box volume must be greater than zero litres."
            )

        if self.driver.fs <= 0:
            raise ValueError("Driver Fs must be greater than zero.")

        if self.driver.qts <= 0:
            raise ValueError("Driver Qts must be greater than zero.")

        if self.driver.vas <= 0:
            raise ValueError("Driver Vas must be greater than zero.")

    def _require_calculated(self) -> None:
        if self.fc_hz is None or self.qtc is None or self.f3_hz is None:
            raise RuntimeError(
                "Simulation has not been calculated. "
                "Call calculate() first."
            )

    @property
    def volume_m3(self) -> float:
        """Internal box volume in cubic metres."""
        return litres_to_cubic_metres(self.volume_l)

    @property
    def alpha(self) -> float:
        """
        Compliance ratio Vas / Vb.

        Vas and Vb can remain in litres because this is a ratio.
        """
        return self.driver.vas / self.volume_l

    def calculate_fc(self) -> float:
        """Calculate sealed-system resonance frequency."""
        return self.driver.fs * math.sqrt(1.0 + self.alpha)

    def calculate_qtc(self) -> float:
        """Calculate sealed-system total Q."""
        return self.driver.qts * math.sqrt(1.0 + self.alpha)

    def calculate_f3(self, fc_hz: float, qtc: float) -> float:
        """Calculate the -3 dB frequency of the sealed system."""
        coefficient = 2.0 - (1.0 / qtc**2)

        frequency_ratio_squared = (
            -coefficient + math.sqrt(coefficient**2 + 4.0)
        ) / 2.0

        frequency_ratio = math.sqrt(frequency_ratio_squared)

        return fc_hz * frequency_ratio

    def calculate_transfer_function(
        self,
        frequencies_hz: np.ndarray,
    ) -> np.ndarray:
        """
        Calculate normalized sealed-box transfer-function magnitude.

        Parameters
        ----------
        frequencies_hz:
            One-dimensional frequency array in hertz.

        Returns
        -------
        np.ndarray:
            Relative transfer-function magnitude in decibels,
            normalized to 0 dB at high frequency.
        """
        self._require_calculated()

        frequencies_hz = np.asarray(frequencies_hz, dtype=float)

        if frequencies_hz.ndim != 1:
            raise ValueError("Frequency input must be one-dimensional.")

        if np.any(frequencies_hz <= 0):
            raise ValueError("All frequencies must be greater than zero.")

        frequency_ratio = frequencies_hz / self.fc_hz

        numerator = frequency_ratio**4

        denominator = (
            (1.0 - frequency_ratio**2) ** 2
            + (frequency_ratio / self.qtc) ** 2
        )

        magnitude = np.sqrt(numerator / denominator)

        # Avoid log10(0) if extremely small numerical values occur.
        magnitude = np.maximum(magnitude, np.finfo(float).tiny)

        return 20.0 * np.log10(magnitude)

    def plot_transfer_function(
        self,
        minimum_frequency_hz: float = 10.0,
        maximum_frequency_hz: float = 1000.0,
        points: int = 1000,
    ) -> None:
        """Plot normalized transfer-function magnitude."""
        self._require_calculated()

        if minimum_frequency_hz <= 0:
            raise ValueError(
                "Minimum frequency must be greater than zero."
            )

        if maximum_frequency_hz <= minimum_frequency_hz:
            raise ValueError(
                "Maximum frequency must exceed minimum frequency."
            )

        if points < 2:
            raise ValueError("At least two frequency points are required.")

        frequencies_hz = np.logspace(
            np.log10(minimum_frequency_hz),
            np.log10(maximum_frequency_hz),
            points,
        )

        magnitude_db = self.calculate_transfer_function(frequencies_hz)

        plt.figure(figsize=(9, 5))
        plt.semilogx(frequencies_hz, magnitude_db)

        plt.axhline(-3.0, linestyle="--", linewidth=1)
        plt.axhline(0.0, linestyle=":", linewidth=1)

        plt.axvline(
            self.fc_hz,
            linestyle=":",
            linewidth=1,
            label=f"Fc = {self.fc_hz:.1f} Hz",
        )

        plt.axvline(
            self.f3_hz,
            linestyle="--",
            linewidth=1,
            label=f"F3 = {self.f3_hz:.1f} Hz",
        )

        plt.xlabel("Frequency (Hz)")
        plt.ylabel("Transfer function magnitude (dB)")
        plt.title(
            f"{self.driver.manufacturer} {self.driver.model}\n"
            f"Sealed box: {self.volume_l:.1f} L, "
            f"Qtc: {self.qtc:.3f}"
        )

        plt.xlim(minimum_frequency_hz, maximum_frequency_hz)
        plt.ylim(-30.0, 6.0)
        plt.grid(True, which="both")
        plt.legend()
        plt.tight_layout()
        plt.show()

    def calculate(self) -> None:
        """Calculate the principal sealed-box parameters."""
        self.fc_hz = self.calculate_fc()
        self.qtc = self.calculate_qtc()
        self.f3_hz = self.calculate_f3(
            fc_hz=self.fc_hz,
            qtc=self.qtc,
        )

    def summary(self) -> None:
        self._require_calculated()

        print("=" * 50)
        print("Sealed-box simulation")
        print("=" * 50)
        print(
            f"Driver     : "
            f"{self.driver.manufacturer} {self.driver.model}"
        )
        print(f"Box volume : {self.volume_l:.2f} L")
        print(f"Alpha      : {self.alpha:.3f}")
        print(f"Fc         : {self.fc_hz:.2f} Hz")
        print(f"Qtc        : {self.qtc:.3f}")
        print(f"F3         : {self.f3_hz:.2f} Hz")