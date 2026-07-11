import math

from acoustics.bass_reflex_port import (
    BassReflexPortCalculator,
)
from core.enclosures.bass_reflex import (
    BassReflexEnclosure,
)


def test_calculate_required_port_length() -> None:
    enclosure = BassReflexEnclosure(
        volume_l=20.0,
        tuning_hz=38.0,
        port_diameter_mm=68.0,
        port_count=1,
    )

    calculator = BassReflexPortCalculator()

    result = calculator.calculate_required_length(
        enclosure
    )

    assert result.physical_length_mm > 0
    assert result.effective_length_mm > result.physical_length_mm
    assert result.total_port_area_cm2 > 0
    assert result.port_count == 1


def test_length_and_tuning_are_consistent() -> None:
    original_enclosure = BassReflexEnclosure(
        volume_l=20.0,
        tuning_hz=38.0,
        port_diameter_mm=68.0,
        port_count=1,
    )

    calculator = BassReflexPortCalculator()

    result = calculator.calculate_required_length(
        original_enclosure
    )

    enclosure_with_length = BassReflexEnclosure(
        volume_l=20.0,
        tuning_hz=38.0,
        port_diameter_mm=68.0,
        port_count=1,
        port_length_mm=result.physical_length_mm,
    )

    calculated_tuning = calculator.calculate_tuning(
        enclosure_with_length
    )

    assert math.isclose(
        calculated_tuning,
        38.0,
        rel_tol=1e-9,
    )


def test_two_ports_require_more_length_than_one_port() -> None:
    calculator = BassReflexPortCalculator()

    one_port = BassReflexEnclosure(
        volume_l=20.0,
        tuning_hz=38.0,
        port_diameter_mm=68.0,
        port_count=1,
    )

    two_ports = BassReflexEnclosure(
        volume_l=20.0,
        tuning_hz=38.0,
        port_diameter_mm=68.0,
        port_count=2,
    )

    one_port_result = calculator.calculate_required_length(
        one_port
    )

    two_port_result = calculator.calculate_required_length(
        two_ports
    )

    assert (
        two_port_result.physical_length_mm
        > one_port_result.physical_length_mm
    )