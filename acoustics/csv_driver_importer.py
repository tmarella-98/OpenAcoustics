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
    """Summary of a completed CSV import."""

    imported_count: int
    failed_count: int
    errors: list[str]


class CsvDriverImporter:
    """Import loudspeaker driver records from CSV into SQLite."""

    def __init__(self, database: DriverDatabase) -> None:
        self.database = database

    def import_file(
        self,
        file_path: str | Path,
    ) -> CsvImportResult:
        """
        Import all valid rows from a CSV file.

        Missing numerical cells are stored as None, which SQLite stores
        as NULL. Invalid rows are skipped and reported in the result.
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(
                f"CSV file does not exist: {file_path}"
            )

        if not file_path.is_file():
            raise ValueError(
                f"CSV path is not a file: {file_path}"
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
                    normalized_row = self._normalize_row(row)

                    # Ignore fully blank lines.
                    if not any(normalized_row.values()):
                        continue

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
    def _normalize_row(
        row: dict[str, str | None],
    ) -> dict[str, str]:
        """Normalize CSV column names and strip cell whitespace."""
        normalized_row: dict[str, str] = {}

        for key, value in row.items():
            if key is None:
                continue

            normalized_key = key.strip().lower()

            if value is None:
                normalized_value = ""
            else:
                normalized_value = value.strip()

            normalized_row[normalized_key] = normalized_value

        return normalized_row

    @staticmethod
    def _row_to_driver(
        row: dict[str, str],
    ) -> Driver:
        """Convert one normalized CSV row into a Driver."""
        manufacturer = row.get(
            "manufacturer",
            "",
        ).strip()

        model = row.get(
            "model",
            "",
        ).strip()

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
            fs=CsvDriverImporter._optional_float(
                row.get("fs"),
                "Fs",
            ),
            qts=CsvDriverImporter._optional_float(
                row.get("qts"),
                "Qts",
            ),
            qes=CsvDriverImporter._optional_float(
                row.get("qes"),
                "Qes",
            ),
            qms=CsvDriverImporter._optional_float(
                row.get("qms"),
                "Qms",
            ),
            vas=CsvDriverImporter._optional_float(
                row.get("vas"),
                "Vas",
            ),
            re=CsvDriverImporter._optional_float(
                row.get("re"),
                "Re",
            ),
            le=CsvDriverImporter._optional_float(
                row.get("le"),
                "Le",
                allow_zero=True,
            ),
            sd=CsvDriverImporter._optional_float(
                row.get("sd"),
                "Sd",
            ),
            xmax=CsvDriverImporter._optional_float(
                row.get("xmax"),
                "Xmax",
                allow_zero=True,
            ),
            bl=CsvDriverImporter._optional_float(
                row.get("bl"),
                "BL",
                allow_zero=True,
            ),
            mms=CsvDriverImporter._optional_float(
                row.get("mms"),
                "Mms",
            ),
            cms=CsvDriverImporter._optional_float(
                row.get("cms"),
                "Cms",
            ),
        )

    @staticmethod
    def _optional_float(
        value: str | None,
        field_name: str,
        allow_zero: bool = False,
    ) -> float | None:
        """
        Parse an optional numerical field.

        Blank values return None. Non-blank values must be valid numbers.
        """
        if value is None or not str(value).strip():
            return None

        cleaned_value = str(value).strip()

        try:
            number = float(cleaned_value)

        except ValueError as error:
            raise ValueError(
                f"{field_name} must be numeric, "
                f"got '{value}'."
            ) from error

        if allow_zero:
            if number < 0:
                raise ValueError(
                    f"{field_name} cannot be negative."
                )

        elif number <= 0:
            raise ValueError(
                f"{field_name} must be greater than zero."
            )

        return number