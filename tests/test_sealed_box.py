import math

from acoustics.driver import Driver
from acoustics.sealed_box import SealedBox


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