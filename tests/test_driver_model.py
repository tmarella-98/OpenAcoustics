import math

from acoustics.driver import Driver
from acoustics.driver_model import DriverModel


def create_driver() -> Driver:
    return Driver(
        manufacturer="Test",
        model="165",
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
        cms=0.001,
    )


def test_driver_model_properties() -> None:
    model = DriverModel(
        create_driver()
    )

    assert model.fs == 40.0
    assert model.qts == 0.40
    assert model.re == 5.7
    assert model.bl == 7.2


def test_omega_s() -> None:
    model = DriverModel(
        create_driver()
    )

    expected = (
        2.0
        * math.pi
        * 40.0
    )

    assert math.isclose(
        model.omega_s,
        expected,
    )


def test_rms() -> None:
    model = DriverModel(
        create_driver()
    )

    expected = (
        model.omega_s
        * model.mms
        / model.qms
    )

    assert math.isclose(
        model.rms,
        expected,
    )


def test_kms() -> None:
    model = DriverModel(
        create_driver()
    )

    expected = (
        1.0
        / model.cms
    )

    assert math.isclose(
        model.kms,
        expected,
    )