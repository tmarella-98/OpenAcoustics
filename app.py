from acoustics.driver import Driver
from acoustics.project import Project
from acoustics.requirements import Requirements


requirements = Requirements(
    application="6.5-inch Studio Monitor",
    target_f3_hz=48.0,
    target_spl_db=108.0,
    max_box_volume_l=10.0,
    nominal_impedance_ohm=8.0,
    max_driver_diameter_mm=165.0,
    max_cost_usd=30.0,
    max_thd_percent=1.0,
)

project = Project(
    name="Studio Monitor Concept",
    requirements=requirements,
)

driver = Driver.load("examples/SB17NBAC35-8.json")

project.add_driver(driver)

project.summary()