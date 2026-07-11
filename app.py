from acoustics.driver_database import DriverDatabase
from core.project import Project


database = DriverDatabase()
drivers = database.load_all()

project = Project(
    name="Studio Monitor Concept",
)

if drivers:
    project.set_driver(drivers[0])

project.set_sealed_box(
    volume_l=10.0,
)

project.notes = (
    "Initial sealed-box concept for evaluation."
)

project.save(
    "projects/studio_monitor.oa-project"
)

loaded_project = Project.load(
    "projects/studio_monitor.oa-project"
)

loaded_project.summary()