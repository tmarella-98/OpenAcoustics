from acoustics.driver import Driver
from acoustics.driver_database import DriverDatabase


database = DriverDatabase()

driver = Driver.load("examples/SB17NBAC35-8.json")
database.add_driver(driver)

print("Search results for SB:")
print("-" * 40)

for result in database.search("SB"):
    print(f"{result.manufacturer} {result.model}")

print()
print("Drivers with Fs <= 40 Hz and Sd >= 120 cm²:")
print("-" * 40)

for result in database.filter_by_specs(fs_max=40, sd_min=120):
    print(f"{result.manufacturer} {result.model}")