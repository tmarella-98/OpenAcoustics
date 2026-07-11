from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from acoustics.driver import Driver
from core.enclosures.base import Enclosure
from core.enclosures.bass_reflex import BassReflexEnclosure
from core.enclosures.sealed import SealedEnclosure


PROJECT_FORMAT_VERSION = 2


@dataclass
class Project:
    """Represents one OpenAcoustics engineering project."""

    name: str
    driver: Driver | None = None
    enclosure: Enclosure | None = None
    notes: str = ""
    format_version: int = PROJECT_FORMAT_VERSION

    def set_driver(self, driver: Driver) -> None:
        """Assign a driver to the project."""
        self.driver = driver

    def clear_driver(self) -> None:
        """Remove the selected driver."""
        self.driver = None

    def set_enclosure(
        self,
        enclosure: Enclosure,
    ) -> None:
        """Assign an enclosure definition to the project."""
        self.enclosure = enclosure

    def set_sealed_enclosure(
        self,
        volume_l: float,
    ) -> None:
        """Assign a sealed enclosure to the project."""
        self.enclosure = SealedEnclosure(
            volume_l=volume_l
        )

    def set_bass_reflex_enclosure(
        self,
        volume_l: float,
        tuning_hz: float,
        port_diameter_mm: float,
        port_count: int = 1,
        port_length_mm: float | None = None,
    ) -> None:
        """Assign a bass-reflex enclosure to the project."""
        self.enclosure = BassReflexEnclosure(
            volume_l=volume_l,
            tuning_hz=tuning_hz,
            port_diameter_mm=port_diameter_mm,
            port_count=port_count,
            port_length_mm=port_length_mm,
        )

    def clear_enclosure(self) -> None:
        """Remove the enclosure definition."""
        self.enclosure = None

    def to_dict(self) -> dict:
        """Convert the project into JSON-compatible data."""
        return {
            "format_version": self.format_version,
            "name": self.name,
            "driver": (
                self.driver.to_dict()
                if self.driver is not None
                else None
            ),
            "enclosure": (
                self.enclosure.to_dict()
                if self.enclosure is not None
                else None
            ),
            "notes": self.notes,
        }

    @classmethod
    def from_dict(
        cls,
        data: dict,
    ) -> "Project":
        """Create a Project from dictionary data."""
        format_version = data.get(
            "format_version",
            1,
        )

        if format_version not in {1, 2}:
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

        if format_version == 1:
            enclosure = cls._load_version_one_enclosure(
                data
            )
        else:
            enclosure = cls._load_enclosure(
                data.get("enclosure")
            )

        return cls(
            name=data["name"],
            driver=driver,
            enclosure=enclosure,
            notes=data.get("notes", ""),
            format_version=PROJECT_FORMAT_VERSION,
        )

    @staticmethod
    def _load_version_one_enclosure(
        data: dict,
    ) -> Enclosure | None:
        """Migrate the original project enclosure format."""
        enclosure_type = data.get(
            "enclosure_type"
        )

        parameters = data.get(
            "enclosure_parameters",
            {},
        )

        if enclosure_type is None:
            return None

        if enclosure_type == "sealed":
            return SealedEnclosure(
                volume_l=float(
                    parameters["volume_l"]
                )
            )

        raise ValueError(
            "Unsupported version-one enclosure type: "
            f"{enclosure_type}"
        )

    @staticmethod
    def _load_enclosure(
        data: dict | None,
    ) -> Enclosure | None:
        """Create the correct enclosure object from project data."""
        if data is None:
            return None

        enclosure_type = data.get("type")

        if enclosure_type == "sealed":
            return SealedEnclosure.from_dict(data)

        if enclosure_type == "bass_reflex":
            return BassReflexEnclosure.from_dict(data)

        raise ValueError(
            "Unsupported enclosure type: "
            f"{enclosure_type}"
        )

    def save(
        self,
        file_path: str | Path,
    ) -> None:
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

        if self.enclosure is None:
            print("Enclosure: None")

        elif isinstance(
            self.enclosure,
            SealedEnclosure,
        ):
            print("Enclosure: Sealed")
            print(
                f"Volume: "
                f"{self.enclosure.volume_l:.2f} L"
            )

        elif isinstance(
            self.enclosure,
            BassReflexEnclosure,
        ):
            print("Enclosure: Bass reflex")
            print(
                f"Volume: "
                f"{self.enclosure.volume_l:.2f} L"
            )
            print(
                f"Tuning: "
                f"{self.enclosure.tuning_hz:.2f} Hz"
            )
            print(
                f"Port diameter: "
                f"{self.enclosure.port_diameter_mm:.2f} mm"
            )
            print(
                f"Port count: "
                f"{self.enclosure.port_count}"
            )
            print(
                f"Port length: "
                f"{self.enclosure.port_length_mm}"
            )

        if self.notes:
            print(f"Notes: {self.notes}")