from dataclasses import dataclass

import numpy as np

from acoustics.driver_model import DriverModel


@dataclass
class ImpedanceResult:
    """Electrical impedance calculated over frequency."""

    frequency_hz: np.ndarray
    complex_impedance_ohm: np.ndarray

    @property
    def magnitude_ohm(self) -> np.ndarray:
        """Return impedance magnitude in ohms."""
        return np.abs(self.complex_impedance_ohm)

    @property
    def phase_deg(self) -> np.ndarray:
        """Return impedance phase in degrees."""
        return np.angle(
            self.complex_impedance_ohm,
            deg=True,
        )


@dataclass
class ImpedanceCalculator:
    """
    Calculate the small-signal free-air electrical impedance.

    Model components:

    - Re: DC voice-coil resistance
    - Le: voice-coil inductance
    - Bl: electromechanical force factor
    - Mms: moving mass
    - Cms: mechanical compliance
    - Rms: mechanical resistance derived from Fs, Mms and Qms

    This initial implementation uses a simple series Le model.
    Frequency-dependent eddy-current losses are not yet included.
    """

    model: DriverModel

    def calculate(
        self,
        frequencies_hz: np.ndarray,
    ) -> ImpedanceResult:
        """Calculate complex free-air impedance versus frequency."""
        frequencies_hz = np.asarray(
            frequencies_hz,
            dtype=float,
        )

        self._validate_frequencies(
            frequencies_hz
        )

        angular_frequency = (
            2.0
            * np.pi
            * frequencies_hz
        )

        mechanical_impedance = (
            self.model.rms
            + 1j
            * angular_frequency
            * self.model.mms
            + 1.0
            / (
                1j
                * angular_frequency
                * self.model.cms
            )
        )

        motional_impedance = (
            self.model.bl**2
            / mechanical_impedance
        )

        blocked_coil_impedance = (
            self.model.re
            + 1j
            * angular_frequency
            * self.model.le_h
        )

        total_impedance = (
            blocked_coil_impedance
            + motional_impedance
        )

        return ImpedanceResult(
            frequency_hz=frequencies_hz,
            complex_impedance_ohm=total_impedance,
        )

    @staticmethod
    def _validate_frequencies(
        frequencies_hz: np.ndarray,
    ) -> None:
        if frequencies_hz.ndim != 1:
            raise ValueError(
                "Frequency input must be one-dimensional."
            )

        if frequencies_hz.size == 0:
            raise ValueError(
                "Frequency input cannot be empty."
            )

        if not np.all(
            np.isfinite(frequencies_hz)
        ):
            raise ValueError(
                "All frequencies must be finite."
            )

        if np.any(frequencies_hz <= 0):
            raise ValueError(
                "All frequencies must be greater than zero."
            )