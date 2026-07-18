import matplotlib.pyplot as plt
import numpy as np

from acoustics.driver_database import (
    DriverDatabase,
)
from acoustics.driver_model import DriverModel
from acoustics.impedance import (
    ImpedanceCalculator,
)


database = DriverDatabase()
drivers = database.load_all()

if not drivers:
    raise RuntimeError(
        "No drivers exist in the database."
    )

driver = drivers[0]

model = DriverModel(driver)
calculator = ImpedanceCalculator(model)

frequencies_hz = np.logspace(
    np.log10(5.0),
    np.log10(20_000.0),
    2000,
)

result = calculator.calculate(
    frequencies_hz
)

plt.figure(figsize=(10, 6))

plt.semilogx(
    result.frequency_hz,
    result.magnitude_ohm,
    label="Impedance magnitude",
)

plt.axvline(
    model.fs,
    linestyle="--",
    linewidth=1,
    label=f"Fs = {model.fs:.1f} Hz",
)

plt.xlabel("Frequency (Hz)")
plt.ylabel("Impedance magnitude (Ω)")

plt.title(
    f"{driver.manufacturer} "
    f"{driver.model}\n"
    "Free-air electrical impedance"
)

plt.xlim(5.0, 20_000.0)
plt.grid(True, which="both")
plt.legend()
plt.tight_layout()
plt.show()