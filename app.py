import matplotlib.pyplot as plt
import numpy as np

from acoustics.bass_reflex import BassReflex
from acoustics.driver_database import DriverDatabase
from core.enclosures.bass_reflex import (
    BassReflexEnclosure,
)


database = DriverDatabase()
drivers = database.load_all()

if not drivers:
    raise RuntimeError(
        "No drivers exist in the database."
    )

driver = drivers[0]

enclosure = BassReflexEnclosure(
    volume_l=20.0,
    tuning_hz=38.0,
    port_diameter_mm=68.0,
)

simulation = BassReflex(
    driver=driver,
    enclosure=enclosure,
)

simulation.calculate()
simulation.summary()

frequencies_hz = np.logspace(
    np.log10(10.0),
    np.log10(1000.0),
    1000,
)

magnitude_db = (
    simulation.calculate_transfer_function(
        frequencies_hz
    )
)

plt.semilogx(
    frequencies_hz,
    magnitude_db,
)

plt.axhline(
    0.0,
    linestyle=":",
)

plt.axhline(
    -3.0,
    linestyle="--",
)

plt.axvline(
    enclosure.tuning_hz,
    linestyle=":",
    label=f"Fb = {enclosure.tuning_hz:.1f} Hz",
)

plt.xlabel("Frequency (Hz)")
plt.ylabel("Transfer function magnitude (dB)")
plt.title(
    f"{driver.manufacturer} {driver.model}\n"
    "Bass-reflex transfer function"
)
plt.xlim(10.0, 1000.0)
plt.ylim(-40.0, 10.0)
plt.grid(True, which="both")
plt.legend()
plt.tight_layout()
plt.show()