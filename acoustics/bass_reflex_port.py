import math
from dataclasses import dataclass

from core.enclosures.bass_reflex import BassReflexEnclosure


DEFAULT_SPEED_OF_SOUND_M_S = 343.0


@dataclass(frozen=True)
class PortGeometryResult:
    """Calculated geometry and tuning information for a bass-reflex port."""

    tuning_hz: float
    physical_length_mm: float
    effective_length_mm: float
    total_port_area_cm2: float
    single_port_area_cm2: float
    port_count: int


class BassReflexPortCalculator:
    """
    Calculate circular bass-reflex port length and tuning.

    This is an initial lossless Helmholtz model. Port losses, enclosure
    leakage, wall proximity and nonlinear flow are not yet included.
    """

    def __init__(
        self,
        speed_of_sound_m_s: float = DEFAULT_SPEED_OF_SOUND_M_S,
        end_correction_factor: float = 1.46,
    ) -> None:
        if speed_of_sound_m_s <= 0:
            raise ValueError(
                "Speed of sound must be greater than zero."
            )

        if end_correction_factor < 0:
            raise ValueError(
                "End-correction factor cannot be negative."
            )

        self.speed_of_sound_m_s = speed_of_sound_m_s
        self.end_correction_factor = end_correction_factor

    def calculate_required_length(
        self,
        enclosure: BassReflexEnclosure,
    ) -> PortGeometryResult:
        """Calculate port length required to achieve the selected tuning."""
        volume_m3 = self._litres_to_cubic_metres(
            enclosure.volume_l
        )

        radius_m = self._millimetres_to_metres(
            enclosure.port_diameter_mm
        ) / 2.0

        single_port_area_m2 = math.pi * radius_m**2

        total_port_area_m2 = (
            single_port_area_m2
            * enclosure.port_count
        )

        angular_wave_number = (
            2.0
            * math.pi
            * enclosure.tuning_hz
            / self.speed_of_sound_m_s
        )

        effective_length_m = (
            total_port_area_m2
            / (
                volume_m3
                * angular_wave_number**2
            )
        )

        end_correction_m = (
            self.end_correction_factor
            * radius_m
        )

        physical_length_m = (
            effective_length_m
            - end_correction_m
        )

        if physical_length_m <= 0:
            raise ValueError(
                "Calculated physical port length is zero or negative. "
                "The selected tuning, volume and port geometry are "
                "not practical with this end-correction model."
            )

        return PortGeometryResult(
            tuning_hz=enclosure.tuning_hz,
            physical_length_mm=(
                physical_length_m * 1000.0
            ),
            effective_length_mm=(
                effective_length_m * 1000.0
            ),
            total_port_area_cm2=(
                total_port_area_m2 * 10_000.0
            ),
            single_port_area_cm2=(
                single_port_area_m2 * 10_000.0
            ),
            port_count=enclosure.port_count,
        )

    def calculate_tuning(
        self,
        enclosure: BassReflexEnclosure,
    ) -> float:
        """
        Calculate tuning frequency from an enclosure with a supplied
        physical port length.
        """
        if enclosure.port_length_mm is None:
            raise ValueError(
                "Port length is required to calculate tuning frequency."
            )

        volume_m3 = self._litres_to_cubic_metres(
            enclosure.volume_l
        )

        radius_m = self._millimetres_to_metres(
            enclosure.port_diameter_mm
        ) / 2.0

        single_port_area_m2 = math.pi * radius_m**2

        total_port_area_m2 = (
            single_port_area_m2
            * enclosure.port_count
        )

        physical_length_m = self._millimetres_to_metres(
            enclosure.port_length_mm
        )

        effective_length_m = (
            physical_length_m
            + self.end_correction_factor * radius_m
        )

        tuning_hz = (
            self.speed_of_sound_m_s
            / (2.0 * math.pi)
            * math.sqrt(
                total_port_area_m2
                / (
                    volume_m3
                    * effective_length_m
                )
            )
        )

        return tuning_hz

    @staticmethod
    def _litres_to_cubic_metres(
        value_l: float,
    ) -> float:
        return value_l / 1000.0

    @staticmethod
    def _millimetres_to_metres(
        value_mm: float,
    ) -> float:
        return value_mm / 1000.0