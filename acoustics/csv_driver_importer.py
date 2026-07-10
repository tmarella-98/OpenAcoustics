import csv
from dataclasses import dataclass
from pathlib import Path

from acoustics.driver import Driver
from acoustics.driver_database import DriverDatabase


REQUIRED_COLUMNS = {
    "manufacturer",
    "model",
    "fs",
    "qts",
    "qes",
    "qms",
    "vas",
    "re",
    "le",
    "sd",
    "xmax",
    "bl",
    "mms",
    "cms",
}


@dataclass
class CsvImportResult:
    imported_count: int
    failed_count: int
    errors: list[str]


class CsvDriverImporter:
    """Import loudspeaker driver data from CSV into SQLite."""

    def __init__(self, database: DriverDatabase) -> None:
        self.database = database

    def import_file(
        self,
        file_path: str | Path,
    ) -> CsvImportResult:
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(
                f"CSV file does not exist: {file_path}"
            )

        imported_count = 0
        failed_count = 0
        errors: list[str] = []

        with file_path.open(
            "r",
            encoding="utf-8-sig",
            newline="",
        ) as csv_file:
            reader = csv.DictReader(csv_file)

            if reader.fieldnames is None:
                raise ValueError(
                    "CSV file does not contain a header row."
                )

            normalized_headers = {
                header.strip().lower()
                for header in reader.fieldnames
                if header is not None
            }

            missing_columns = (
                REQUIRED_COLUMNS - normalized_headers
            )

            if missing_columns:
                missing_text = ", ".join(
                    sorted(missing_columns)
                )

                raise ValueError(
                    "CSV is missing required columns: "
                    f"{missing_text}"
                )

            for row_number, row in enumerate(
                reader,
                start=2,
            ):
                try:
                    normalized_row = {
                        str(key).strip().lower(): (
                            value.strip()
                            if isinstance(value, str)
                            else value
                        )
                        for key, value in row.items()
                        if key is not None
                    }

                    driver = self._row_to_driver(
                        normalized_row
                    )

                    self.database.add_driver(driver)
                    imported_count += 1

                except Exception as error:
                    failed_count += 1
                    errors.append(
                        f"Row {row_number}: {error}"
                    )

        return CsvImportResult(
            imported_count=imported_count,
            failed_count=failed_count,
            errors=errors,
        )

    @staticmethod
    def _row_to_driver(
        row: dict[str, str],
    ) -> Driver:
        manufacturer = row["manufacturer"].strip()
        model = row["model"].strip()

        if not manufacturer:
            raise ValueError(
                "Manufacturer cannot be empty."
            )

        if not model:
            raise ValueError(
                "Model cannot be empty."
            )

        return Driver(
            manufacturer=manufacturer,
            model=model,
            fs=CsvDriverImporter._positive_float(
                row["fs"],
                "Fs",
            ),
            qts=CsvDriverImporter._positive_float(
                row["qts"],
                "Qts",
            ),
            qes=CsvDriverImporter._positive_float(
                row["qes"],
                "Qes",
            ),
            qms=CsvDriverImporter._positive_float(
                row["qms"],
                "Qms",
            ),
            vas=CsvDriverImporter._positive_float(
                row["vas"],
                "Vas",
            ),
            re=CsvDriverImporter._positive_float(
                row["re"],
                "Re",
            ),
            le=CsvDriverImporter._non_negative_float(
                row["le"],
                "Le",
            ),
            sd=CsvDriverImporter._positive_float(
                row["sd"],
                "Sd",
            ),
            xmax=CsvDriverImporter._non_negative_float(
                row["xmax"],
                "Xmax",
            ),
            bl=CsvDriverImporter._non_negative_float(
                row["bl"],
                "BL",
            ),
            mms=CsvDriverImporter._positive_float(
                row["mms"],
                "Mms",
            ),
            cms=CsvDriverImporter._positive_float(
                row["cms"],
                "Cms",
            ),
        )

    @staticmethod
    def _positive_float(
        value: str,
        field_name: str,
    ) -> float:
        number = CsvDriverImporter._parse_float(
            value,
            field_name,
        )

        if number <= 0:
            raise ValueError(
                f"{field_name} must be greater than zero."
            )

        return number

    @staticmethod
    def _non_negative_float(
        value: str,
        field_name: str,
    ) -> float:
        number = CsvDriverImporter._parse_float(
            value,
            field_name,
        )

        if number < 0:
            raise ValueError(
                f"{field_name} cannot be negative."
            )

        return number

    @staticmethod
    def _parse_float(
        value: str,
        field_name: str,
    ) -> float:
        if value is None or not str(value).strip():
            raise ValueError(
                f"{field_name} is missing."
            )

        try:
            return float(value)

        except ValueError as error:
            raise ValueError(
                f"{field_name} must be numeric, "
                f"got '{value}'."
            ) from error