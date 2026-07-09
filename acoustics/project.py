from dataclasses import dataclass, field

from acoustics.driver import Driver
from acoustics.requirements import Requirements


@dataclass
class Project:
    """Represents an electroacoustic design project."""

    name: str
    requirements: Requirements
    drivers: list[Driver] = field(default_factory=list)

    def add_driver(self, driver: Driver) -> None:
        self.drivers.append(driver)

    def summary(self) -> None:
        print("=" * 50)
        print(f"Project: {self.name}")
        print("=" * 50)

        self.requirements.summary()

        print()
        print("Drivers")
        print("-" * 40)

        if not self.drivers:
            print("No drivers added yet.")
            return

        for index, driver in enumerate(self.drivers, start=1):
            print(f"{index}. {driver.manufacturer} {driver.model}")