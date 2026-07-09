from dataclasses import dataclass


@dataclass
class Requirements:
    """Defines target performance requirements for a loudspeaker project."""

    application: str
    profile: str = "hifi_woofer"

    target_f3_hz: float | None = None
    target_spl_db: float | None = None
    max_box_volume_l: float | None = None
    nominal_impedance_ohm: float | None = None
    max_driver_diameter_mm: float | None = None
    max_cost_usd: float | None = None
    max_thd_percent: float | None = None

    def summary(self) -> None:
        print("Requirements")
        print("-" * 40)
        print(f"Application          : {self.application}")
        print(f"Profile              : {self.profile}")
        print(f"Target F3            : {self.target_f3_hz} Hz")
        print(f"Target SPL           : {self.target_spl_db} dB")
        print(f"Max box volume       : {self.max_box_volume_l} L")
        print(f"Nominal impedance    : {self.nominal_impedance_ohm} Ω")
        print(f"Max driver diameter  : {self.max_driver_diameter_mm} mm")
        print(f"Max cost             : ${self.max_cost_usd}")
        print(f"Max THD              : {self.max_thd_percent} %")