from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class Driver:
    """Represents a loudspeaker driver."""

    manufacturer: str
    model: str

    fs: float | None = None
    qts: float | None = None
    qes: float | None = None
    qms: float | None = None
    vas: float | None = None

    re: float | None = None
    le: float | None = None

    sd: float | None = None
    xmax: float | None = None
    bl: float | None = None
    mms: float | None = None
    cms: float | None = None

    @staticmethod
    def _format_value(
        value: float | None,
        unit: str = "",
    ) -> str:
        if value is None:
            return "N/A"

        return f"{value} {unit}".strip()

    def summary(self) -> None:
        print("=" * 40)
        print(f"{self.manufacturer} {self.model}")
        print("=" * 40)
        print(f"Fs   : {self._format_value(self.fs, 'Hz')}")
        print(f"Qts  : {self._format_value(self.qts)}")
        print(f"Qes  : {self._format_value(self.qes)}")
        print(f"Qms  : {self._format_value(self.qms)}")
        print(f"Vas  : {self._format_value(self.vas, 'L')}")
        print(f"Re   : {self._format_value(self.re, 'Ω')}")
        print(f"Le   : {self._format_value(self.le, 'mH')}")
        print(f"Sd   : {self._format_value(self.sd, 'cm²')}")
        print(f"Xmax : {self._format_value(self.xmax, 'mm')}")
        print(f"BL   : {self._format_value(self.bl, 'N/A')}")
        print(f"Mms  : {self._format_value(self.mms, 'g')}")
        print(f"Cms  : {self._format_value(self.cms, 'mm/N')}")

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Driver":
        return cls(**data)

    def save(self, file_path: str | Path) -> None:
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with file_path.open("w", encoding="utf-8") as file:
            json.dump(self.to_dict(), file, indent=4)

    @classmethod
    def load(cls, file_path: str | Path) -> "Driver":
        file_path = Path(file_path)

        with file_path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        return cls.from_dict(data)