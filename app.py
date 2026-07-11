from acoustics.bass_reflex_port import (
    BassReflexPortCalculator,
)
from core.enclosures.bass_reflex import (
    BassReflexEnclosure,
)


enclosure = BassReflexEnclosure(
    volume_l=20.0,
    tuning_hz=38.0,
    port_diameter_mm=68.0,
    port_count=1,
)

calculator = BassReflexPortCalculator()

result = calculator.calculate_required_length(
    enclosure
)

print("=" * 50)
print("Bass-reflex port calculation")
print("=" * 50)
print(f"Tuning              : {result.tuning_hz:.2f} Hz")
print(f"Port count          : {result.port_count}")
print(f"Single-port area    : {result.single_port_area_cm2:.2f} cm²")
print(f"Total port area     : {result.total_port_area_cm2:.2f} cm²")
print(f"Effective length    : {result.effective_length_mm:.2f} mm")
print(f"Physical length     : {result.physical_length_mm:.2f} mm")