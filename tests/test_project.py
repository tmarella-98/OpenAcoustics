from pathlib import Path

from acoustics.driver import Driver
from core.project import Project


def test_project_save_and_load(
    tmp_path: Path,
) -> None:
    driver = Driver(
        manufacturer="Test Audio",
        model="T165",
        fs=35.0,
        qts=0.35,
        vas=30.0,
    )

    project = Project(
        name="Test Project",
        driver=driver,
        notes="Test notes",
    )

    project.set_sealed_box(
        volume_l=12.0,
    )

    file_path = (
        tmp_path / "test_project.oa-project"
    )

    project.save(file_path)

    loaded_project = Project.load(file_path)

    assert loaded_project.name == "Test Project"
    assert loaded_project.driver is not None
    assert loaded_project.driver.model == "T165"
    assert loaded_project.enclosure_type == "sealed"
    assert (
        loaded_project.enclosure_parameters["volume_l"]
        == 12.0
    )
    assert loaded_project.notes == "Test notes"


def test_project_can_exist_without_driver() -> None:
    project = Project(
        name="Requirements Only Project"
    )

    assert project.driver is None
    assert project.enclosure_type is None