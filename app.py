from acoustics.driver import Driver
from acoustics.driver_library import DriverLibrary


library = DriverLibrary()

driver = Driver.load("examples/SB17NBAC35-8.json")

saved_path = library.add_driver(driver)

print(f"Saved driver to: {saved_path}")

print()
print("All drivers in library:")
print("-" * 40)

for driver in library.load_all():
    print(f"{driver.manufacturer} {driver.model}")

print()
print("Search results for 'SB':")
print("-" * 40)

for driver in library.search("SB"):
    print(f"{driver.manufacturer} {driver.model}")