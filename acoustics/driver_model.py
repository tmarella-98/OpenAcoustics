from dataclasses import dataclass
import math

from acoustics.driver import Driver


@dataclass(frozen=True)
class DriverModel:
    """
    Physical loudspeaker model.

    This class derives useful mechanical and electrical parameters
    from the Thiele/Small parameters stored in the driver database.
    """

    driver: Driver

    @property
    def fs(self) -> float:
        return self._require(self.driver.fs, "Fs")

    @property
    def qts(self) -> float:
        return self._require(self.driver.qts, "Qts")

    @property
    def qes(self) -> float:
        return self._require(self.driver.qes, "Qes")

    @property
    def qms(self) -> float:
        return self._require(self.driver.qms, "Qms")

    @property
    def vas(self) -> float:
        return self._require(self.driver.vas, "Vas")

    @property
    def re(self) -> float:
        return self._require(self.driver.re, "Re")

    @property
    def le(self) -> float:
        return self._require(self.driver.le, "Le")

    @property
    def bl(self) -> float:
        return self._require(self.driver.bl, "Bl")

    @property
    def sd(self) -> float:
        return self._require(self.driver.sd, "Sd")

    @property
    def xmax(self) -> float:
        return self._require(self.driver.xmax, "Xmax")

    @property
    def mms(self) -> float:
        """
        Moving mass (kg)

        Stored in the database as grams.
        """
        return (
            self._require(
                self.driver.mms,
                "Mms",
            )
            / 1000.0
        )

    @property
    def cms(self) -> float:
        """
        Mechanical compliance (m/N)

        Stored in the database as mm/N.
        """
        return (
            self._require(
                self.driver.cms,
                "Cms",
            )
            / 1000.0
        )

    @property
    def omega_s(self) -> float:
        """Angular resonance."""
        return (
            2.0
            * math.pi
            * self.fs
        )

    @property
    def rms(self) -> float:
        """
        Mechanical resistance (N·s/m)

        Derived from Fs, Mms and Qms.
        """
        return (
            self.omega_s
            * self.mms
            / self.qms
        )

    @property
    def kms(self) -> float:
        """
        Mechanical stiffness (N/m)
        """
        return 1.0 / self.cms

    @property
    def compliance_volume_ratio(self) -> float:
        """
        Useful helper for future enclosure calculations.
        """
        return self.vas

    @staticmethod
    def _require(
        value: float | None,
        name: str,
    ) -> float:
        if value is None:
            raise ValueError(
                f"{name} is required."
            )

        return float(value)