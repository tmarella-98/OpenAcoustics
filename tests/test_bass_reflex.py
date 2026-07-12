import math

import numpy as np
import pytest

from acoustics.bass_reflex import BassReflex
from acoustics.driver import Driver
from core.enclosures.bass_reflex import (
    BassReflexEnclosure,
)


def create_test_driver() -> Driver:
    return Driver(
        manufacturer="Test Audio",
        model="BR165",
        fs=35.0,
        qts=0.35,
        vas=30.0,
    )


def create_test_enclosure() -> BassReflexEnclosure:
    return BassReflexEnclosure(
        volume_l=20.0,
        tuning_hz=40.0,
        port_diameter_mm=68.0,
    )


def test_calculate_normalized_parameters() -> None:
    simulation = BassReflex(
        driver=create_test_driver(),
        enclosure=create_test_enclosure(),
    )

    simulation.calculate()

    assert math.isclose(
        simulation.alpha,
        30.0 / 20.0,
        rel_tol=1e-12,
    )

    assert math.isclose(
        simulation.tuning_ratio,
        40.0 / 35.0,
        rel_tol=1e-12,
    )


def test_transfer_function_approaches_zero_db() -> None:
    simulation = BassReflex(
        driver=create_test_driver(),
        enclosure=create_test_enclosure(),
    )

    simulation.calculate()

    response_db = (
        simulation.calculate_transfer_function(
            np.array([1_000_000.0])
        )
    )

    assert math.isclose(
        response_db[0],
        0.0,
        abs_tol=0.01,
    )


def test_missing_vas_is_rejected() -> None:
    driver = Driver(
        manufacturer="Test Audio",
        model="Incomplete",
        fs=35.0,
        qts=0.35,
        vas=None,
    )

    with pytest.raises(
        ValueError,
        match="Vas is missing",
    ):
        BassReflex(
            driver=driver,
            enclosure=create_test_enclosure(),
        )