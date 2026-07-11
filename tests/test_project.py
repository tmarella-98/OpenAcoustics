from pathlib import Path

from acoustics.driver import Driver
from core.enclosures.bass_reflex import BassReflexEnclosure
from core.enclosures.sealed import SealedEnclosure
from core.project import Project


def test_project_can_exist_without_driver_or_enclosure() -> None:
    project = Project(
        name="Requirements Only Project"
    )

    assert project.name == "Requirements Only Project"
    assert project.driver is None
    assert project.enclosure is None
    assert project.notes == ""


def test_project_can_assign_and_clear_driver() -> None:
    driver = Driver(
        manufacturer="Test Audio",
        model="T165",
        fs=35.0,
        qts=0.35,
        vas=30.0,
    )

    project = Project(
        name="Driver Assignment Test"
    )

    project.set_driver(driver)

    assert project.driver is driver
    assert project.driver.model == "T165"

    project.clear_driver()

    assert project.driver is None


def test_project_can_assign_sealed_enclosure() -> None:
    project = Project(
        name="Sealed Project"
    )

    project.set_sealed_enclosure(
        volume_l=12.0
    )

    assert isinstance(
        project.enclosure,
        SealedEnclosure,
    )

    assert project.enclosure.volume_l == 12.0


def test_project_can_assign_bass_reflex_enclosure() -> None:
    project = Project(
        name="Bass Reflex Project"
    )

    project.set_bass_reflex_enclosure(
        volume_l=20.0,
        tuning_hz=38.0,
        port_diameter_mm=68.0,
        port_count=1,
        port_length_mm=180.0,
    )

    assert isinstance(
        project.enclosure,
        BassReflexEnclosure,
    )

    assert project.enclosure.volume_l == 20.0
    assert project.enclosure.tuning_hz == 38.0
    assert project.enclosure.port_diameter_mm == 68.0
    assert project.enclosure.port_count == 1
    assert project.enclosure.port_length_mm == 180.0


def test_project_can_clear_enclosure() -> None:
    project = Project(
        name="Clear Enclosure Test"
    )

    project.set_sealed_enclosure(
        volume_l=10.0
    )

    assert project.enclosure is not None

    project.clear_enclosure()

    assert project.enclosure is None


def test_sealed_project_save_and_load(
    tmp_path: Path,
) -> None:
    driver = Driver(
        manufacturer="Test Audio",
        model="T165",
        fs=35.0,
        qts=0.35,
        qes=0.40,
        qms=5.0,
        vas=30.0,
        re=5.8,
        le=0.4,
        sd=135.0,
        xmax=6.0,
        bl=7.5,
        mms=15.0,
        cms=1.5,
    )

    project = Project(
        name="Test Sealed Project",
        driver=driver,
        notes="Test notes",
    )

    project.set_sealed_enclosure(
        volume_l=12.0
    )

    file_path = (
        tmp_path / "sealed_project.oa-project"
    )

    project.save(file_path)

    loaded_project = Project.load(file_path)

    assert loaded_project.name == "Test Sealed Project"
    assert loaded_project.driver is not None
    assert loaded_project.driver.manufacturer == "Test Audio"
    assert loaded_project.driver.model == "T165"
    assert loaded_project.driver.fs == 35.0
    assert loaded_project.notes == "Test notes"

    assert isinstance(
        loaded_project.enclosure,
        SealedEnclosure,
    )

    assert loaded_project.enclosure.volume_l == 12.0


def test_bass_reflex_project_save_and_load(
    tmp_path: Path,
) -> None:
    driver = Driver(
        manufacturer="Test Audio",
        model="BR200",
        fs=30.0,
        qts=0.38,
        vas=55.0,
    )

    project = Project(
        name="Bass Reflex Test",
        driver=driver,
    )

    project.set_bass_reflex_enclosure(
        volume_l=20.0,
        tuning_hz=38.0,
        port_diameter_mm=68.0,
        port_count=2,
        port_length_mm=180.0,
    )

    file_path = (
        tmp_path / "bass_reflex.oa-project"
    )

    project.save(file_path)

    loaded_project = Project.load(file_path)

    assert loaded_project.name == "Bass Reflex Test"
    assert loaded_project.driver is not None
    assert loaded_project.driver.model == "BR200"

    assert isinstance(
        loaded_project.enclosure,
        BassReflexEnclosure,
    )

    assert loaded_project.enclosure.volume_l == 20.0
    assert loaded_project.enclosure.tuning_hz == 38.0
    assert loaded_project.enclosure.port_diameter_mm == 68.0
    assert loaded_project.enclosure.port_count == 2
    assert loaded_project.enclosure.port_length_mm == 180.0


def test_project_save_creates_parent_folder(
    tmp_path: Path,
) -> None:
    project = Project(
        name="Nested Project"
    )

    file_path = (
        tmp_path
        / "nested"
        / "folder"
        / "project.oa-project"
    )

    project.save(file_path)

    assert file_path.exists()


def test_project_loads_version_one_sealed_enclosure() -> None:
    old_project_data = {
        "format_version": 1,
        "name": "Legacy Project",
        "driver": None,
        "enclosure_type": "sealed",
        "enclosure_parameters": {
            "volume_l": 15.0,
        },
        "notes": "Old project format",
    }

    project = Project.from_dict(
        old_project_data
    )

    assert project.name == "Legacy Project"
    assert project.format_version == 2
    assert project.notes == "Old project format"

    assert isinstance(
        project.enclosure,
        SealedEnclosure,
    )

    assert project.enclosure.volume_l == 15.0