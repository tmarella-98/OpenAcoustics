from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

from acoustics.driver import Driver


PROJECT_FORMAT_VERSION = 1


@dataclass
class Project:
    """Represents one OpenAcoustics engineering project."""

    name: str

    driver: Driver | None = None

    enclosure_type: str | None = None
    enclosure_parameters: dict[str, float] = field(
        default_factory=dict
    )

    notes: str = ""

    format_version: int = PROJECT_FORMAT_VERSION

    def set_driver(self, driver: Driver) -> None:
        """Assign a driver to the project."""
        self.driver = driver

    def clear_driver(self) -> None:
        """Remove the currently selected driver."""
        self.driver = None

    def set_sealed_box(self, volume_l: float) -> None:
        """Configure a sealed enclosure for the project."""
        if volume_l <= 0:
            raise ValueError(
                "Sealed-box volume must be greater than zero."
            )

        self.enclosure_type = "sealed"
        self.enclosure_parameters = {
            "volume_l": volume_l,
        }

    def clear_enclosure(self) -> None:
        """Remove the current enclosure configuration."""
        self.enclosure_type = None
        self.enclosure_parameters = {}

    def to_dict(self) -> dict:
        """Convert the project into JSON-compatible data."""
        project_data = asdict(self)

        if self.driver is not None:
            project_data["driver"] = self.driver.to_dict()

        return project_data

    @classmethod
    def from_dict(cls, data: dict) -> "Project":
        """Create a Project from dictionary data."""
        format_version = data.get(
            "format_version",
            PROJECT_FORMAT_VERSION,
        )

        if format_version != PROJECT_FORMAT_VERSION:
            raise ValueError(
                "Unsupported project format version: "
                f"{format_version}"
            )

        driver_data = data.get("driver")

        driver = (
            Driver.from_dict(driver_data)
            if driver_data is not None
            else None
        )

        return cls(
            name=data["name"],
            driver=driver,
            enclosure_type=data.get("enclosure_type"),
            enclosure_parameters=data.get(
                "enclosure_parameters",
                {},
            ),
            notes=data.get("notes", ""),
            format_version=format_version,
        )

    def save(self, file_path: str | Path) -> None:
        """Save the project to an OpenAcoustics project file."""
        file_path = Path(file_path)

        file_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with file_path.open(
            "w",
            encoding="utf-8",
        ) as project_file:
            json.dump(
                self.to_dict(),
                project_file,
                indent=4,
            )

    @classmethod
    def load(
        cls,
        file_path: str | Path,
    ) -> "Project":
        """Load an OpenAcoustics project file."""
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(
                f"Project file does not exist: {file_path}"
            )

        with file_path.open(
            "r",
            encoding="utf-8",
        ) as project_file:
            data = json.load(project_file)

        return cls.from_dict(data)

    def summary(self) -> None:
        """Print a concise project summary."""
        print("=" * 50)
        print(f"Project: {self.name}")
        print("=" * 50)

        if self.driver is None:
            print("Driver: None")
        else:
            print(
                "Driver: "
                f"{self.driver.manufacturer} "
                f"{self.driver.model}"
            )

        print(
            f"Enclosure type: "
            f"{self.enclosure_type or 'None'}"
        )

        if self.enclosure_parameters:
            print("Enclosure parameters:")

            for name, value in self.enclosure_parameters.items():
                print(f"  {name}: {value}")

        if self.notes:
            print(f"Notes: {self.notes}")