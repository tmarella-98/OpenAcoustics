from dataclasses import dataclass

from core.enclosures.base import Enclosure


@dataclass
class BassReflexEnclosure(Enclosure):
    """Defines a bass-reflex enclosure and its vent geometry."""

    volume_l: float
    tuning_hz: float

    port_diameter_mm: float
    port_count: int = 1

    port_length_mm: float | None = None

    def __post_init__(self) -> None:
        if self.volume_l <= 0:
            raise ValueError(
                "Bass-reflex enclosure volume must be greater than zero."
            )

        if self.tuning_hz <= 0:
            raise ValueError(
                "Bass-reflex tuning frequency must be greater than zero."
            )

        if self.port_diameter_mm <= 0:
            raise ValueError(
                "Port diameter must be greater than zero."
            )

        if self.port_count < 1:
            raise ValueError(
                "Port count must be at least one."
            )

        if (
            self.port_length_mm is not None
            and self.port_length_mm <= 0
        ):
            raise ValueError(
                "Port length must be greater than zero when supplied."
            )

    @property
    def enclosure_type(self) -> str:
        return "bass_reflex"

    def to_dict(self) -> dict:
        return {
            "type": self.enclosure_type,
            "volume_l": self.volume_l,
            "tuning_hz": self.tuning_hz,
            "port_diameter_mm": self.port_diameter_mm,
            "port_count": self.port_count,
            "port_length_mm": self.port_length_mm,
        }

    @classmethod
    def from_dict(
        cls,
        data: dict,
    ) -> "BassReflexEnclosure":
        port_length = data.get("port_length_mm")

        return cls(
            volume_l=float(data["volume_l"]),
            tuning_hz=float(data["tuning_hz"]),
            port_diameter_mm=float(
                data["port_diameter_mm"]
            ),
            port_count=int(
                data.get("port_count", 1)
            ),
            port_length_mm=(
                float(port_length)
                if port_length is not None
                else None
            ),
        )