import math
import numpy as np
from acoustics.driver import Driver
from acoustics.sealed_box import SealedBox
import pytest


def test_sealed_box_fc_and_qtc() -> None:
    driver = Driver(
        manufacturer="Test",
        model="Driver",
        fs=33.0,
        qts=0.33,
        qes=0.36,
        qms=4.0,
        vas=33.0,
        re=5.8,
        le=0.4,
        sd=138.0,
        xmax=5.5,
        bl=7.2,
        mms=14.0,
        cms=1.7,
    )

    simulation = SealedBox(driver=driver, volume_l=10.0)
    simulation.calculate()

    expected_multiplier = math.sqrt(1.0 + 33.0 / 10.0)

    assert math.isclose(
        simulation.fc_hz,
        33.0 * expected_multiplier,
        rel_tol=1e-9,
    )

    assert math.isclose(
        simulation.qtc,
        0.33 * expected_multiplier,
        rel_tol=1e-9,
    )
    


def test_transfer_function_approaches_zero_db_at_high_frequency() -> None:
    driver = Driver(
        manufacturer="Test",
        model="Driver",
        fs=33.0,
        qts=0.33,
        qes=0.36,
        qms=4.0,
        vas=33.0,
        re=5.8,
        le=0.4,
        sd=138.0,
        xmax=5.5,
        bl=7.2,
        mms=14.0,
        cms=1.7,
    )

    simulation = SealedBox(driver=driver, volume_l=10.0)
    simulation.calculate()

    magnitude_db = simulation.calculate_transfer_function(
        np.array([100_000.0])
    )

    assert math.isclose(
        magnitude_db[0],
        0.0,
        abs_tol=0.01,
    )


def test_transfer_function_is_minus_three_db_at_f3() -> None:
    driver = Driver(
        manufacturer="Test",
        model="Driver",
        fs=33.0,
        qts=0.33,
        qes=0.36,
        qms=4.0,
        vas=33.0,
        re=5.8,
        le=0.4,
        sd=138.0,
        xmax=5.5,
        bl=7.2,
        mms=14.0,
        cms=1.7,
    )

    simulation = SealedBox(driver=driver, volume_l=10.0)
    simulation.calculate()

    magnitude_db = simulation.calculate_transfer_function(
        np.array([simulation.f3_hz])
    )

    assert math.isclose(
        magnitude_db[0],
        -3.0103,
        abs_tol=0.01,
    )
def test_driver_can_store_missing_parameters() -> None:
    driver = Driver(
        manufacturer="Test Audio",
        model="Incomplete Tweeter",
        fs=900.0,
        re=5.8,
    )

    assert driver.fs == 900.0
    assert driver.qts is None
    assert driver.vas is None



def test_sealed_box_rejects_missing_vas() -> None:
    driver = Driver(
        manufacturer="Test Audio",
        model="Incomplete Driver",
        fs=40.0,
        qts=0.4,
        vas=None,
    )

    with pytest.raises(
        ValueError,
        match="Vas is missing",
    ):
        SealedBox(
            driver=driver,
            volume_l=10.0,
        )