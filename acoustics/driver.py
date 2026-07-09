from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class Driver:
    """Represents a loudspeaker driver."""

    manufacturer: str
    model: str

    fs: float
    qts: float
    qes: float
    qms: float

    vas: float

    re: float
    le: float

    sd: float
    xmax: float
    bl: float
    mms: float
    cms: float

    def summary(self) -> None:
        print("=" * 40)
        print(f"{self.manufacturer} {self.model}")
        print("=" * 40)
        print(f"Fs   : {self.fs} Hz")
        print(f"Qts  : {self.qts}")
        print(f"Qes  : {self.qes}")
        print(f"Qms  : {self.qms}")
        print(f"Vas  : {self.vas} L")
        print(f"Re   : {self.re} Ω")
        print(f"Le   : {self.le} mH")
        print(f"Sd   : {self.sd} cm²")
        print(f"Xmax : {self.xmax} mm")
        print(f"BL   : {self.bl} N/A")
        print(f"Mms  : {self.mms} g")
        print(f"Cms  : {self.cms} mm/N")

    def to_dict(self) -> dict:
        """Convert driver object to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Driver":
        """Create driver object from dictionary."""
        return cls(**data)

    def save(self, file_path: str | Path) -> None:
        """Save driver data to a JSON file."""
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with file_path.open("w", encoding="utf-8") as file:
            json.dump(self.to_dict(), file, indent=4)

    @classmethod
    def load(cls, file_path: str | Path) -> "Driver":
        """Load driver data from a JSON file."""
        file_path = Path(file_path)

        with file_path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        return cls.from_dict(data)