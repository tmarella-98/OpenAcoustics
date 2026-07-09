from pathlib import Path

from acoustics.driver import Driver
from acoustics.web_search import open_datasheet_search


class DriverLibrary:
    """Local file-based loudspeaker driver database."""

    def __init__(self, library_path: str = "library/drivers"):
        self.library_path = Path(library_path)
        self.library_path.mkdir(parents=True, exist_ok=True)

    def _driver_path(self, driver: Driver) -> Path:
        manufacturer_folder = driver.manufacturer.strip().replace("/", "-")
        model_file = driver.model.strip().replace("/", "-") + ".json"
        return self.library_path / manufacturer_folder / model_file

    def add_driver(self, driver: Driver) -> Path:
        path = self._driver_path(driver)
        driver.save(path)
        return path

    def load_all(self) -> list[Driver]:
        drivers = []

        for file_path in self.library_path.rglob("*.json"):
            try:
                drivers.append(Driver.load(file_path))
            except Exception as error:
                print(f"Could not load {file_path}: {error}")

        return drivers

    def search(self, query: str) -> list[Driver]:
        query = query.lower()
        results = []

        for driver in self.load_all():
            text = f"{driver.manufacturer} {driver.model}".lower()

            if query in text:
                results.append(driver)

        return results

    def search_or_open_web(self, query: str) -> list[Driver]:
        results = self.search(query)

        if results:
            return results

        print(f"No local drivers found for: {query}")
        print("Opening datasheet web search...")
        open_datasheet_search(query)
        return []