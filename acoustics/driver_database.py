import sqlite3
from pathlib import Path

from acoustics.driver import Driver


class DriverDatabase:
    """SQLite-backed searchable driver database."""

    def __init__(self, database_path: str = "library/openacoustics.db"):
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._create_tables()

    def _connect(self):
        return sqlite3.connect(self.database_path)

    def _create_tables(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS drivers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    manufacturer TEXT NOT NULL,
                    model TEXT NOT NULL,
                    fs REAL,
                    qts REAL,
                    qes REAL,
                    qms REAL,
                    vas REAL,
                    re REAL,
                    le REAL,
                    sd REAL,
                    xmax REAL,
                    bl REAL,
                    mms REAL,
                    cms REAL,
                    UNIQUE(manufacturer, model)
                )
                """
            )

    def add_driver(self, driver: Driver) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO drivers (
                    manufacturer, model,
                    fs, qts, qes, qms,
                    vas, re, le, sd, xmax, bl, mms, cms
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    driver.manufacturer,
                    driver.model,
                    driver.fs,
                    driver.qts,
                    driver.qes,
                    driver.qms,
                    driver.vas,
                    driver.re,
                    driver.le,
                    driver.sd,
                    driver.xmax,
                    driver.bl,
                    driver.mms,
                    driver.cms,
                ),
            )

    def search(self, query: str) -> list[Driver]:
        query = f"%{query}%"

        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT manufacturer, model,
                       fs, qts, qes, qms,
                       vas, re, le, sd, xmax, bl, mms, cms
                FROM drivers
                WHERE manufacturer LIKE ?
                   OR model LIKE ?
                ORDER BY manufacturer, model
                """,
                (query, query),
            ).fetchall()

        return [self._row_to_driver(row) for row in rows]

    def filter_by_specs(
        self,
        fs_max: float | None = None,
        qts_min: float | None = None,
        qts_max: float | None = None,
        xmax_min: float | None = None,
        sd_min: float | None = None,
    ) -> list[Driver]:
        conditions = []
        values = []

        if fs_max is not None:
            conditions.append("fs <= ?")
            values.append(fs_max)

        if qts_min is not None:
            conditions.append("qts >= ?")
            values.append(qts_min)

        if qts_max is not None:
            conditions.append("qts <= ?")
            values.append(qts_max)

        if xmax_min is not None:
            conditions.append("xmax >= ?")
            values.append(xmax_min)

        if sd_min is not None:
            conditions.append("sd >= ?")
            values.append(sd_min)

        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)

        with self._connect() as connection:
            rows = connection.execute(
                f"""
                SELECT manufacturer, model,
                       fs, qts, qes, qms,
                       vas, re, le, sd, xmax, bl, mms, cms
                FROM drivers
                {where_clause}
                ORDER BY manufacturer, model
                """,
                values,
            ).fetchall()

        return [self._row_to_driver(row) for row in rows]
    def load_all(self) -> list[Driver]:
     """Load every driver stored in the database."""
     with self._connect() as connection:
        rows = connection.execute(
            """
            SELECT manufacturer, model,
                   fs, qts, qes, qms,
                   vas, re, le, sd, xmax, bl, mms, cms
            FROM drivers
            ORDER BY manufacturer, model
            """
        ).fetchall()

        return [self._row_to_driver(row) for row in rows]
    @staticmethod
    def _row_to_driver(row) -> Driver:
        return Driver(
            manufacturer=row[0],
            model=row[1],
            fs=row[2],
            qts=row[3],
            qes=row[4],
            qms=row[5],
            vas=row[6],
            re=row[7],
            le=row[8],
            sd=row[9],
            xmax=row[10],
            bl=row[11],
            mms=row[12],
            cms=row[13],
        )