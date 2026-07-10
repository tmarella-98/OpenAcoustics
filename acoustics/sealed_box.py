import math
from dataclasses import dataclass, field

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
            raise ValueError("Sealed-box volume must be greater than zero litres.")

        if self.driver.fs <= 0:
            raise ValueError("Driver Fs must be greater than zero.")

        if self.driver.qts <= 0:
            raise ValueError("Driver Qts must be greater than zero.")

        if self.driver.vas <= 0:
            raise ValueError("Driver Vas must be greater than zero.")

    @property
    def volume_m3(self) -> float:
        """Internal box volume in cubic metres."""
        return litres_to_cubic_metres(self.volume_l)

    @property
    def alpha(self) -> float:
        """
        Compliance ratio Vas / Vb.

        Vas and Vb may both remain in litres because this is a ratio.
        """
        return self.driver.vas / self.volume_l

    def calculate_fc(self) -> float:
        """Calculate sealed-system resonance frequency."""
        return self.driver.fs * math.sqrt(1.0 + self.alpha)

    def calculate_qtc(self) -> float:
        """Calculate sealed-system total Q."""
        return self.driver.qts * math.sqrt(1.0 + self.alpha)

    def calculate_f3(self, fc_hz: float, qtc: float) -> float:
        """Calculate the -3 dB frequency of the second-order high-pass system."""
        coefficient = 2.0 - (1.0 / qtc**2)

        frequency_ratio_squared = (
            -coefficient + math.sqrt(coefficient**2 + 4.0)
        ) / 2.0

        frequency_ratio = math.sqrt(frequency_ratio_squared)

        return fc_hz * frequency_ratio

    def calculate(self) -> None:
        """Calculate the principal sealed-box system parameters."""
        self.fc_hz = self.calculate_fc()
        self.qtc = self.calculate_qtc()
        self.f3_hz = self.calculate_f3(
            fc_hz=self.fc_hz,
            qtc=self.qtc,
        )

    def summary(self) -> None:
        if self.fc_hz is None or self.qtc is None or self.f3_hz is None:
            raise RuntimeError(
                "Simulation has not been calculated. Call calculate() first."
            )

        print("=" * 50)
        print("Sealed-box simulation")
        print("=" * 50)
        print(f"Driver     : {self.driver.manufacturer} {self.driver.model}")
        print(f"Box volume : {self.volume_l:.2f} L")
        print(f"Alpha      : {self.alpha:.3f}")
        print(f"Fc         : {self.fc_hz:.2f} Hz")
        print(f"Qtc        : {self.qtc:.3f}")
        print(f"F3         : {self.f3_hz:.2f} Hz")