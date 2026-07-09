from acoustics.driver_library import DriverLibrary


library = DriverLibrary()

query = input("Search driver library: ")

results = library.search_or_open_web(query)

if results:
    print()
    print("Local matches:")
    print("-" * 40)

    for driver in results:
        print(f"{driver.manufacturer} {driver.model}")