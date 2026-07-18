import math

import numpy as np
import pytest

from acoustics.driver import Driver
from acoustics.driver_model import DriverModel
from acoustics.impedance import (
    ImpedanceCalculator,
)


def create_test_model() -> DriverModel:
    driver = Driver(
        manufacturer="Test Audio",
        model="T165",
        fs=40.0,
        qts=0.40,
        qes=0.45,
        qms=5.0,
        vas=25.0,
        re=5.7,
        le=0.45,
        sd=135.0,
        xmax=5.5,
        bl=7.2,
        mms=15.0,
        cms=1.055428996,
    )

    return DriverModel(driver)


def test_impedance_result_shapes() -> None:
    model = create_test_model()
    calculator = ImpedanceCalculator(model)

    frequencies_hz = np.array(
        [10.0, 40.0, 100.0, 1000.0]
    )

    result = calculator.calculate(
        frequencies_hz
    )

    assert result.frequency_hz.shape == (4,)
    assert (
        result.complex_impedance_ohm.shape
        == (4,)
    )
    assert result.magnitude_ohm.shape == (4,)
    assert result.phase_deg.shape == (4,)


def test_impedance_is_finite() -> None:
    model = create_test_model()
    calculator = ImpedanceCalculator(model)

    frequencies_hz = np.logspace(
        np.log10(1.0),
        np.log10(20_000.0),
        2000,
    )

    result = calculator.calculate(
        frequencies_hz
    )

    assert np.all(
        np.isfinite(result.magnitude_ohm)
    )

    assert np.all(
        np.isfinite(result.phase_deg)
    )


def test_low_frequency_impedance_approaches_re() -> None:
    model = create_test_model()
    calculator = ImpedanceCalculator(model)

    result = calculator.calculate(
        np.array([0.001])
    )

    assert math.isclose(
        result.magnitude_ohm[0],
        model.re,
        abs_tol=0.01,
    )


def test_resonance_creates_impedance_peak() -> None:
    model = create_test_model()
    calculator = ImpedanceCalculator(model)

    frequencies_hz = np.array(
        [
            model.fs / 4.0,
            model.fs,
            model.fs * 4.0,
        ]
    )

    result = calculator.calculate(
        frequencies_hz
    )

    resonance_impedance = (
        result.magnitude_ohm[1]
    )

    assert resonance_impedance > (
        result.magnitude_ohm[0]
    )

    assert resonance_impedance > (
        result.magnitude_ohm[2]
    )


def test_impedance_at_resonance_matches_model() -> None:
    model = create_test_model()
    calculator = ImpedanceCalculator(model)

    result = calculator.calculate(
        np.array([model.fs])
    )

    angular_frequency = (
        2.0
        * math.pi
        * model.fs
    )

    expected_complex_impedance = (
        model.re
        + 1j
        * angular_frequency
        * model.le_h
        + model.bl**2 / model.rms
    )

    assert np.isclose(
        result.complex_impedance_ohm[0],
        expected_complex_impedance,
        rtol=1e-6,
    )


def test_non_positive_frequency_is_rejected() -> None:
    model = create_test_model()
    calculator = ImpedanceCalculator(model)

    with pytest.raises(
        ValueError,
        match="greater than zero",
    ):
        calculator.calculate(
            np.array([0.0, 100.0])
        )