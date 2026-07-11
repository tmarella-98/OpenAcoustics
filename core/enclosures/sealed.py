from dataclasses import dataclass

from core.enclosures.base import Enclosure


@dataclass
class SealedEnclosure(Enclosure):
    """Defines a sealed loudspeaker enclosure."""

    volume_l: float

    def __post_init__(self) -> None:
        if self.volume_l <= 0:
            raise ValueError(
                "Sealed enclosure volume must be greater than zero."
            )

    @property
    def enclosure_type(self) -> str:
        return "sealed"

    def to_dict(self) -> dict:
        return {
            "type": self.enclosure_type,
            "volume_l": self.volume_l,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SealedEnclosure":
        return cls(
            volume_l=float(data["volume_l"]),
        )