from acoustics.driver_database import DriverDatabase
from acoustics.driver_matcher import DriverMatcher
from acoustics.requirements import Requirements


requirements = Requirements(
    application="6.5-inch Studio Monitor",
    profile="microspeaker",
    target_f3_hz=48.0,
    target_spl_db=108.0,
    max_box_volume_l=10.0,
    nominal_impedance_ohm=8.0,
    max_driver_diameter_mm=165.0,
    max_cost_usd=30.0,
    max_thd_percent=1.0,
)

database = DriverDatabase()
drivers = database.search("SB")

matcher = DriverMatcher()

for driver in drivers:
    result = matcher.match(driver, requirements)
    result.summary()
    result.plot_scores()